from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user
from sqlalchemy import func
from extensions import db
from models import Session, SessionRequest, SkillOffering, CreditTransaction, Review, Report

sessions_bp = Blueprint('sessions', __name__)

def participant(session):
    return current_user.id in [session.request.learner_id, session.request.offering.teacher_id]

def update_rating(user_id):
    average = db.session.query(func.avg(Review.rating)).filter(Review.reviewee_id == user_id).scalar()
    from models import User
    user = User.query.get(user_id)
    user.average_rating = float(average or 0)

@sessions_bp.route('/sessions/mine', methods=['GET'])
@auth_required('token')
def my_sessions():
    sessions = Session.query.join(SessionRequest).join(SkillOffering).filter(
        (SessionRequest.learner_id == current_user.id) | (SkillOffering.teacher_id == current_user.id)
    ).order_by(Session.scheduled_start.desc()).all()
    return jsonify([item.to_dict(True) for item in sessions]), 200

@sessions_bp.route('/sessions/<int:session_id>', methods=['GET'])
@auth_required('token')
def get_session(session_id):
    session = Session.query.get_or_404(session_id)
    if not participant(session) and not current_user.has_role('admin'):
        return jsonify({'message': 'You cannot view this session'}), 403

    data = session.to_dict(True)
    data['reviews'] = [review.to_dict() for review in session.reviews]
    return jsonify(data), 200

@sessions_bp.route('/sessions/<int:session_id>/cancel', methods=['PATCH'])
@auth_required('token')
def cancel_session(session_id):
    session = Session.query.get_or_404(session_id)

    if not participant(session) and not current_user.has_role('admin'):
        return jsonify({'message': 'You cannot cancel this session'}), 403
    if session.status not in ['SCHEDULED', 'AWAITING_CONFIRMATION']:
        return jsonify({'message': 'This session cannot be cancelled'}), 409

    item = session.request
    if item.credit_reserved and not session.settled:
        item.learner.credit_balance += item.offering.credit_cost
        item.credit_reserved = False
        db.session.add(CreditTransaction(
            user_id=item.learner_id,
            session_id=session.id,
            amount=item.offering.credit_cost,
            transaction_type='REFUND',
            reason='Credit released after session cancellation'
        ))

    session.status = 'CANCELLED'
    item.status = 'CANCELLED'
    db.session.commit()
    return jsonify({'message': 'Session cancelled', 'session': session.to_dict(True)}), 200

@sessions_bp.route('/sessions/<int:session_id>/confirm', methods=['PATCH'])
@auth_required('token')
def confirm_session(session_id):
    session = Session.query.get_or_404(session_id)

    if not participant(session):
        return jsonify({'message': 'Only participants can confirm completion'}), 403
    if session.status not in ['SCHEDULED', 'AWAITING_CONFIRMATION']:
        return jsonify({'message': 'This session cannot be confirmed'}), 409

    if current_user.id == session.request.offering.teacher_id:
        session.teacher_confirmed = True
    else:
        session.learner_confirmed = True

    session.status = 'AWAITING_CONFIRMATION'
    session.request.status = 'AWAITING_CONFIRMATION'

    if session.teacher_confirmed and session.learner_confirmed:
        session.status = 'COMPLETED'
        session.request.status = 'COMPLETED'
        session.completed_at = datetime.utcnow()

        if not session.settled:
            teacher = session.request.offering.teacher
            teacher.credit_balance += session.request.offering.credit_cost
            session.settled = True
            session.request.credit_reserved = False
            db.session.add(CreditTransaction(
                user_id=teacher.id,
                session_id=session.id,
                amount=session.request.offering.credit_cost,
                transaction_type='EARNED',
                reason='Credits earned for completed session'
            ))

    db.session.commit()
    return jsonify({'message': 'Completion confirmed', 'session': session.to_dict(True)}), 200

@sessions_bp.route('/sessions/<int:session_id>/reviews', methods=['POST'])
@auth_required('token')
def create_review(session_id):
    session = Session.query.get_or_404(session_id)

    if not participant(session):
        return jsonify({'message': 'Only participants can review'}), 403
    if session.status != 'COMPLETED':
        return jsonify({'message': 'Reviews are allowed after completion'}), 409
    if Review.query.filter_by(session_id=session.id, reviewer_id=current_user.id).first():
        return jsonify({'message': 'You already reviewed this session'}), 409

    data = request.get_json() or {}
    try:
        rating = int(data.get('rating'))
    except (TypeError, ValueError):
        return jsonify({'message': 'Rating must be a number'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400

    if current_user.id == session.request.learner_id:
        reviewee_id = session.request.offering.teacher_id
    else:
        reviewee_id = session.request.learner_id

    review = Review(
        session_id=session.id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=rating,
        comment=str(data.get('comment', '')).strip()
    )
    db.session.add(review)
    db.session.flush()
    update_rating(reviewee_id)
    db.session.commit()

    return jsonify({'message': 'Review submitted', 'review': review.to_dict()}), 201

@sessions_bp.route('/credits/transactions', methods=['GET'])
@auth_required('token')
def credit_transactions():
    transactions = CreditTransaction.query.filter_by(user_id=current_user.id).order_by(CreditTransaction.created_at.desc()).all()
    return jsonify({
        'balance': current_user.credit_balance,
        'transactions': [item.to_dict() for item in transactions]
    }), 200

@sessions_bp.route('/reports', methods=['POST'])
@auth_required('token')
def create_report():
    data = request.get_json() or {}
    reported_user_id = data.get('reported_user_id')
    offering_id = data.get('offering_id')
    session_id = data.get('session_id')
    reason = str(data.get('reason', '')).strip()

    if not reason:
        return jsonify({'message': 'Reason is required'}), 400
    if not any([reported_user_id, offering_id, session_id]):
        return jsonify({'message': 'Select a user, offering or session to report'}), 400

    report = Report(
        reporter_id=current_user.id,
        reported_user_id=reported_user_id,
        offering_id=offering_id,
        session_id=session_id,
        reason=reason,
        details=str(data.get('details', '')).strip()
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'message': 'Report submitted', 'report': report.to_dict()}), 201
