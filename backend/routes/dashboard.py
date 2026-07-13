from datetime import datetime
from flask import Blueprint, jsonify
from flask_security import auth_required, current_user
from models import SkillOffering, SessionRequest, Session

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@auth_required('token')
def dashboard():
    incoming = SessionRequest.query.join(SkillOffering).filter(
        SkillOffering.teacher_id == current_user.id,
        SessionRequest.status == 'PENDING'
    ).count()
    outgoing = SessionRequest.query.filter_by(learner_id=current_user.id, status='PENDING').count()
    upcoming = Session.query.join(SessionRequest).join(SkillOffering).filter(
        ((SessionRequest.learner_id == current_user.id) | (SkillOffering.teacher_id == current_user.id)),
        Session.status.in_(['SCHEDULED', 'AWAITING_CONFIRMATION']),
        Session.scheduled_start >= datetime.utcnow()
    ).order_by(Session.scheduled_start.asc()).all()
    completed = Session.query.join(SessionRequest).join(SkillOffering).filter(
        ((SessionRequest.learner_id == current_user.id) | (SkillOffering.teacher_id == current_user.id)),
        Session.status == 'COMPLETED'
    ).count()

    return jsonify({
        'credit_balance': current_user.credit_balance,
        'active_offerings': SkillOffering.query.filter_by(teacher_id=current_user.id, status='ACTIVE').count(),
        'incoming_requests': incoming,
        'outgoing_requests': outgoing,
        'completed_sessions': completed,
        'upcoming_sessions': [item.to_dict(True) for item in upcoming[:5]]
    }), 200
