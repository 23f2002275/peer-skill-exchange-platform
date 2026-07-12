from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user, roles_required
from sqlalchemy import or_
from extensions import db
from models import SkillOffering, Skill

offerings_bp = Blueprint('offerings', __name__)

def can_manage(offering):
    return offering.teacher_id == current_user.id or current_user.has_role('admin')

@offerings_bp.route('', methods=['GET'])
def offerings():
    query = SkillOffering.query.join(Skill).filter(SkillOffering.status == 'ACTIVE')
    keyword = str(request.args.get('keyword', '')).strip()
    skill_id = request.args.get('skill_id')
    category_id = request.args.get('category_id')
    mode = str(request.args.get('mode', '')).strip()
    level = str(request.args.get('level', '')).strip()

    if keyword:
        query = query.filter(or_(SkillOffering.title.ilike(f'%{keyword}%'), Skill.name.ilike(f'%{keyword}%')))
    if skill_id:
        query = query.filter(SkillOffering.skill_id == skill_id)
    if category_id:
        query = query.filter(Skill.category_id == category_id)
    if mode:
        query = query.filter(SkillOffering.teaching_mode == mode)
    if level:
        query = query.filter(SkillOffering.proficiency_level == level)

    page = max(int(request.args.get('page', 1)), 1)
    per_page = min(max(int(request.args.get('per_page', 9)), 1), 50)
    result = query.order_by(SkillOffering.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [item.to_dict() for item in result.items],
        'page': result.page,
        'pages': result.pages,
        'total': result.total
    }), 200

@offerings_bp.route('/mine', methods=['GET'])
@auth_required('token')
@roles_required('member')
def my_offerings():
    items = SkillOffering.query.filter_by(teacher_id=current_user.id).order_by(SkillOffering.created_at.desc()).all()
    return jsonify([item.to_dict(True) for item in items]), 200

@offerings_bp.route('/<int:offering_id>', methods=['GET'])
def offering(offering_id):
    item = SkillOffering.query.get_or_404(offering_id)
    if item.status == 'HIDDEN':
        return jsonify({'message': 'Offering is not available'}), 404
    return jsonify(item.to_dict(True)), 200

@offerings_bp.route('', methods=['POST'])
@auth_required('token')
@roles_required('member')
def create_offering():
    if not current_user.active:
        return jsonify({'message': 'Suspended account cannot create offerings'}), 403

    data = request.get_json() or {}
    required = ['skill_id', 'title', 'proficiency_level', 'teaching_mode', 'duration_minutes']
    if any(data.get(field) in [None, ''] for field in required):
        return jsonify({'message': 'Required offering fields are missing'}), 400

    skill = Skill.query.filter_by(id=data.get('skill_id'), active=True).first()
    if not skill:
        return jsonify({'message': 'Skill not found'}), 404

    try:
        duration = int(data.get('duration_minutes'))
        cost = int(data.get('credit_cost', 1))
    except (TypeError, ValueError):
        return jsonify({'message': 'Duration and credit cost must be numbers'}), 400

    if duration < 15 or duration > 240:
        return jsonify({'message': 'Duration must be between 15 and 240 minutes'}), 400
    if cost < 1 or cost > 5:
        return jsonify({'message': 'Credit cost must be between 1 and 5'}), 400

    item = SkillOffering(
        teacher_id=current_user.id,
        skill_id=skill.id,
        title=str(data.get('title')).strip(),
        description=str(data.get('description', '')).strip(),
        proficiency_level=str(data.get('proficiency_level')).strip(),
        teaching_mode=str(data.get('teaching_mode')).strip(),
        duration_minutes=duration,
        availability_text=str(data.get('availability_text', '')).strip(),
        credit_cost=cost,
        status='ACTIVE'
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Offering created', 'offering': item.to_dict(True)}), 201

@offerings_bp.route('/<int:offering_id>', methods=['PUT'])
@auth_required('token')
def update_offering(offering_id):
    item = SkillOffering.query.get_or_404(offering_id)
    if not can_manage(item):
        return jsonify({'message': 'You cannot edit this offering'}), 403
    if item.status in ['ARCHIVED', 'HIDDEN'] and not current_user.has_role('admin'):
        return jsonify({'message': 'This offering cannot be edited'}), 409

    data = request.get_json() or {}
    skill = Skill.query.filter_by(id=data.get('skill_id', item.skill_id), active=True).first()
    if not skill:
        return jsonify({'message': 'Skill not found'}), 404

    try:
        duration = int(data.get('duration_minutes', item.duration_minutes))
        cost = int(data.get('credit_cost', item.credit_cost))
    except (TypeError, ValueError):
        return jsonify({'message': 'Duration and credit cost must be numbers'}), 400

    if duration < 15 or duration > 240 or cost < 1 or cost > 5:
        return jsonify({'message': 'Invalid duration or credit cost'}), 400

    item.skill_id = skill.id
    item.title = str(data.get('title', item.title)).strip()
    item.description = str(data.get('description', item.description or '')).strip()
    item.proficiency_level = str(data.get('proficiency_level', item.proficiency_level)).strip()
    item.teaching_mode = str(data.get('teaching_mode', item.teaching_mode)).strip()
    item.duration_minutes = duration
    item.availability_text = str(data.get('availability_text', item.availability_text or '')).strip()
    item.credit_cost = cost
    db.session.commit()

    return jsonify({'message': 'Offering updated', 'offering': item.to_dict(True)}), 200

@offerings_bp.route('/<int:offering_id>', methods=['DELETE'])
@auth_required('token')
def delete_offering(offering_id):
    item = SkillOffering.query.get_or_404(offering_id)
    if not can_manage(item):
        return jsonify({'message': 'You cannot delete this offering'}), 403
    if item.requests:
        return jsonify({'message': 'Offering has session history and must be archived'}), 409

    db.session.delete(item)
    db.session.commit()
    return '', 204

@offerings_bp.route('/<int:offering_id>/status', methods=['PATCH'])
@auth_required('token')
def update_status(offering_id):
    item = SkillOffering.query.get_or_404(offering_id)
    if not can_manage(item):
        return jsonify({'message': 'You cannot change this offering'}), 403

    status = str((request.get_json() or {}).get('status', '')).upper()
    allowed = ['ACTIVE', 'PAUSED', 'ARCHIVED']
    if current_user.has_role('admin'):
        allowed.append('HIDDEN')
    if status not in allowed:
        return jsonify({'message': 'Invalid status'}), 400

    item.status = status
    db.session.commit()
    return jsonify({'message': 'Status updated', 'offering': item.to_dict(True)}), 200
