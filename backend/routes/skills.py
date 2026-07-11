from flask import Blueprint, request, jsonify
from models import Skill, SkillCategory

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('', methods=['GET'])
def skills():
    query = Skill.query.filter_by(active=True)
    category_id = request.args.get('category_id')
    keyword = str(request.args.get('keyword', '')).strip()

    if category_id:
        query = query.filter_by(category_id=category_id)
    if keyword:
        query = query.filter(Skill.name.ilike(f'%{keyword}%'))

    return jsonify([skill.to_dict() for skill in query.order_by(Skill.name.asc()).all()]), 200

@skills_bp.route('/categories', methods=['GET'])
def categories():
    items = SkillCategory.query.filter_by(active=True).order_by(SkillCategory.name.asc()).all()
    return jsonify([item.to_dict() for item in items]), 200
