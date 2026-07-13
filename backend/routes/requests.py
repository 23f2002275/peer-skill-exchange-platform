from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user, roles_required
from extensions import db
from models import SkillOffering, SessionRequest, Session, CreditTransaction

requests_bp = Blueprint('requests', __name__)

def parse_datetime(value):
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00')).replace(tzinfo=None)
    except (TypeError, ValueError):
        return None

def has_overlap(user_id, start, duration):
    end = start + timedelta(minutes=duration)
    sessions = Session.query.filter(Session.status.in_(['SCHEDULED', 'AWAITING_CONFIRMATION'])).all()

    for session in sessions:
        teacher_id = session.request.offering.teacher_id
        learner_id = session.request.learner_id
        if user_id not in [teacher_id, learner_id]:
            continue
        old_start = session.scheduled_start
        old_end = old_start + timedelta(minutes=session.duration_minutes)
        if start < old_end and end > old_start:
            return True

    return False

@requests_bp.route('/offerings/<int:offering_id>/requests', methods=['POST'])
@auth_required('token')
@roles_required('member')
def create_request(offering_id):
    offering = SkillOffering.query.get_or_404(offering_id)
    data = request.get_json() or {}

    if not current_user.active:
        return jsonify({'message': 'Suspended account cannot create requests'}), 403
    if offering.status != 'ACTIVE':
        return jsonify({'message': 'Offering is not active'}), 409
    if offering.teacher_id == current_user.id:
        return jsonify({'message': 'You cannot request your own offering'}), 400

    existing = SessionRequest.query.filter(
        SessionRequest.offering_id == offering.id,
        SessionRequest.learner_id == current_user.id,
        SessionRequest.status.in_(['PENDING', 'ACCEPTED', 'SCHEDULED', 'AWAITING_CONFIRMATION'])
    ).first()

    if existing:
        return jsonify({'message': 'You already have an active request for this offering'}), 409

    preferred_time = parse_datetime(data.get('preferred_time'))
    if data.get('preferred_time') and not preferred_time:
        return jsonify({'message': 'Invalid preferred time'}), 400
    if preferred_time and preferred_time <= datetime.utcnow():
        return jsonify({'message': 'Preferred time must be in the future'}), 400

    item = SessionRequest(
        offering_id=offering.id,
        learner_id=current_user.id,
        message=str(data.get('message', '')).strip(),
        preferred_time=preferred_time
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Session request sent', 'request': item.to_dict()}), 201

@requests_bp.route('/requests/mine', methods=['GET'])
@auth_required('token')
def my_requests():
    incoming = SessionRequest.query.join(SkillOffering).filter(SkillOffering.teacher_id == current_user.id).all()
    outgoing = SessionRequest.query.filter_by(learner_id=current_user.id).all()

    return jsonify({
        'incoming': [item.to_dict() for item in sorted(incoming, key=lambda x: x.requested_at, reverse=True)],
        'outgoing': [item.to_dict() for item in sorted(outgoing, key=lambda x: x.requested_at, reverse=True)]
    }), 200

@requests_bp.route('/requests/<int:request_id>/accept', methods=['PATCH'])
@auth_required('token')
@roles_required('member')
def accept_request(request_id):
    item = SessionRequest.query.get_or_404(request_id)

    if item.offering.teacher_id != current_user.id:
        return jsonify({'message': 'You cannot accept this request'}), 403
    if item.status != 'PENDING':
        return jsonify({'message': 'Only pending requests can be accepted'}), 409
    if item.learner.credit_balance < item.offering.credit_cost:
        return jsonify({'message': 'Learner does not have enough credits'}), 409

    item.learner.credit_balance -= item.offering.credit_cost
    item.credit_reserved = True
    item.status = 'ACCEPTED'
    item.decided_at = datetime.utcnow()
    db.session.add(CreditTransaction(
        user_id=item.learner_id,
        amount=-item.offering.credit_cost,
        transaction_type='RESERVED',
        reason='Credit reserved for ' + item.offering.title
    ))
    db.session.commit()

    return jsonify({'message': 'Request accepted and credit reserved', 'request': item.to_dict()}), 200

@requests_bp.route('/requests/<int:request_id>/reject', methods=['PATCH'])
@auth_required('token')
@roles_required('member')
def reject_request(request_id):
    item = SessionRequest.query.get_or_404(request_id)

    if item.offering.teacher_id != current_user.id:
        return jsonify({'message': 'You cannot reject this request'}), 403
    if item.status != 'PENDING':
        return jsonify({'message': 'Only pending requests can be rejected'}), 409

    item.status = 'REJECTED'
    item.decided_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Request rejected', 'request': item.to_dict()}), 200

@requests_bp.route('/requests/<int:request_id>/cancel', methods=['PATCH'])
@auth_required('token')
def cancel_request(request_id):
    item = SessionRequest.query.get_or_404(request_id)
    participant = item.learner_id == current_user.id or item.offering.teacher_id == current_user.id

    if not participant and not current_user.has_role('admin'):
        return jsonify({'message': 'You cannot cancel this request'}), 403
    if item.status not in ['PENDING', 'ACCEPTED']:
        return jsonify({'message': 'This request cannot be cancelled'}), 409

    if item.credit_reserved:
        item.learner.credit_balance += item.offering.credit_cost
        item.credit_reserved = False
        db.session.add(CreditTransaction(
            user_id=item.learner_id,
            amount=item.offering.credit_cost,
            transaction_type='REFUND',
            reason='Credit released after request cancellation'
        ))

    item.status = 'CANCELLED'
    db.session.commit()
    return jsonify({'message': 'Request cancelled', 'request': item.to_dict()}), 200

@requests_bp.route('/requests/<int:request_id>/session', methods=['POST'])
@auth_required('token')
@roles_required('member')
def schedule_session(request_id):
    item = SessionRequest.query.get_or_404(request_id)
    data = request.get_json() or {}

    if item.offering.teacher_id != current_user.id:
        return jsonify({'message': 'Only the teacher can schedule this session'}), 403
    if item.status != 'ACCEPTED':
        return jsonify({'message': 'Request must be accepted first'}), 409
    if item.session:
        return jsonify({'message': 'Session is already scheduled'}), 409

    scheduled_start = parse_datetime(data.get('scheduled_start'))
    if not scheduled_start or scheduled_start <= datetime.utcnow():
        return jsonify({'message': 'Scheduled time must be in the future'}), 400

    duration = item.offering.duration_minutes
    if has_overlap(item.offering.teacher_id, scheduled_start, duration):
        return jsonify({'message': 'Teacher already has a session at this time'}), 409
    if has_overlap(item.learner_id, scheduled_start, duration):
        return jsonify({'message': 'Learner already has a session at this time'}), 409

    session = Session(
        request_id=item.id,
        scheduled_start=scheduled_start,
        duration_minutes=duration,
        meeting_details=str(data.get('meeting_details', '')).strip(),
        status='SCHEDULED'
    )
    item.status = 'SCHEDULED'
    db.session.add(session)
    db.session.commit()
    return jsonify({'message': 'Session scheduled', 'session': session.to_dict(True)}), 201
