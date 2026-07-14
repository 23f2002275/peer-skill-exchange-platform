from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required
from extensions import db
from security_setup import user_datastore
from models import User, SkillCategory, Skill, SkillOffering, Session, Report, CreditTransaction

admin_bp = Blueprint('admin', __name__)

def normalize(value):
    return ' '.join(str(value).strip().split()).title()

@admin_bp.route('/statistics', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def statistics():
    return jsonify({
        'users': User.query.count(),
        'active_users': User.query.filter_by(active=True).count(),
        'skills': Skill.query.count(),
        'active_offerings': SkillOffering.query.filter_by(status='ACTIVE').count(),
        'sessions': Session.query.count(),
        'completed_sessions': Session.query.filter_by(status='COMPLETED').count(),
        'open_reports': Report.query.filter_by(status='OPEN').count()
    }), 200

@admin_bp.route('/users', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def users():
    return jsonify([user.to_dict(True) for user in User.query.order_by(User.created_at.desc()).all()]), 200

@admin_bp.route('/users/<int:user_id>/active', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def update_user_active(user_id):
    user = User.query.get_or_404(user_id)
    active = bool((request.get_json() or {}).get('active'))
    if active:
        user_datastore.activate_user(user)
    else:
        user_datastore.deactivate_user(user)
    db.session.commit()
    return jsonify({'message': 'User status updated', 'user': user.to_dict(True)}), 200

@admin_bp.route('/users/<int:user_id>/credit-adjustments', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def adjust_credit(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    reason = str(data.get('reason', '')).strip()
    try:
        amount = int(data.get('amount'))
    except (TypeError, ValueError):
        return jsonify({'message': 'Amount must be a number'}), 400

    if not reason or amount == 0:
        return jsonify({'message': 'Non-zero amount and reason are required'}), 400
    if user.credit_balance + amount < 0:
        return jsonify({'message': 'Balance cannot become negative'}), 400

    user.credit_balance += amount
    db.session.add(CreditTransaction(
        user_id=user.id,
        amount=amount,
        transaction_type='ADMIN_ADJUSTMENT',
        reason=reason
    ))
    db.session.commit()
    return jsonify({'message': 'Credit balance adjusted', 'user': user.to_dict(True)}), 200

@admin_bp.route('/categories', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def create_category():
    data = request.get_json() or {}
    name = normalize(data.get('name', ''))
    if not name:
        return jsonify({'message': 'Category name is required'}), 400
    if SkillCategory.query.filter(db.func.lower(SkillCategory.name) == name.lower()).first():
        return jsonify({'message': 'Category already exists'}), 409

    category = SkillCategory(name=name, description=str(data.get('description', '')).strip())
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Category created', 'category': category.to_dict()}), 201

@admin_bp.route('/skills', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def create_skill():
    data = request.get_json() or {}
    name = normalize(data.get('name', ''))
    category = SkillCategory.query.get(data.get('category_id'))

    if not name or not category:
        return jsonify({'message': 'Skill name and category are required'}), 400
    if Skill.query.filter(db.func.lower(Skill.name) == name.lower()).first():
        return jsonify({'message': 'Skill already exists'}), 409

    skill = Skill(category_id=category.id, name=name, description=str(data.get('description', '')).strip())
    db.session.add(skill)
    db.session.commit()
    return jsonify({'message': 'Skill created', 'skill': skill.to_dict()}), 201

@admin_bp.route('/offerings', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def offerings():
    items = SkillOffering.query.order_by(SkillOffering.created_at.desc()).all()
    return jsonify([item.to_dict(True) for item in items]), 200

@admin_bp.route('/offerings/<int:offering_id>/visibility', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def offering_visibility(offering_id):
    item = SkillOffering.query.get_or_404(offering_id)
    visible = bool((request.get_json() or {}).get('visible'))
    item.status = 'ACTIVE' if visible else 'HIDDEN'
    db.session.commit()
    return jsonify({'message': 'Offering visibility updated', 'offering': item.to_dict(True)}), 200

@admin_bp.route('/reports', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def reports():
    return jsonify([item.to_dict() for item in Report.query.order_by(Report.created_at.desc()).all()]), 200

@admin_bp.route('/reports/<int:report_id>', methods=['PATCH'])
@auth_required('token')
@roles_required('admin')
def resolve_report(report_id):
    item = Report.query.get_or_404(report_id)
    data = request.get_json() or {}
    status = str(data.get('status', '')).upper()
    if status not in ['RESOLVED', 'DISMISSED']:
        return jsonify({'message': 'Status must be RESOLVED or DISMISSED'}), 400

    item.status = status
    item.admin_notes = str(data.get('admin_notes', '')).strip()
    db.session.commit()
    return jsonify({'message': 'Report updated', 'report': item.to_dict()}), 200
