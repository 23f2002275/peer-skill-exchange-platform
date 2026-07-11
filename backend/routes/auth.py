from uuid import uuid4
from flask import Blueprint, request, jsonify
from flask_security import auth_required, current_user, hash_password
from flask_security.utils import verify_and_update_password
from extensions import db
from security_setup import user_datastore
from models import User, CreditTransaction, SkillOffering, Review

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))
    name = str(data.get('name', '')).strip()

    if not email or not password or not name:
        return jsonify({'message': 'Name, email and password are required'}), 400
    if len(password) < 6:
        return jsonify({'message': 'Password must contain at least 6 characters'}), 400
    if user_datastore.find_user(email=email):
        return jsonify({'message': 'Email already registered'}), 409

    user = user_datastore.create_user(
        email=email,
        password=hash_password(password),
        name=name,
        bio=str(data.get('bio', '')).strip(),
        interests=str(data.get('interests', '')).strip(),
        credit_balance=3,
        roles=['member'],
        fs_uniquifier=uuid4().hex,
    )
    db.session.flush()
    db.session.add(CreditTransaction(
        user_id=user.id,
        amount=3,
        transaction_type='STARTER',
        reason='Starter credits'
    ))
    db.session.commit()

    return jsonify({'message': 'Registration successful', 'user': user.to_dict(True)}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = user_datastore.find_user(email=email)

    if not user or not verify_and_update_password(password, user):
        return jsonify({'message': 'Invalid email or password'}), 401
    if not user.active:
        return jsonify({'message': 'Account is suspended'}), 403

    db.session.commit()
    return jsonify({
        'message': 'Login successful',
        'token': user.get_auth_token(),
        'user': user.to_dict(True)
    }), 200

@auth_bp.route('/me', methods=['GET'])
@auth_required('token')
def me():
    return jsonify(current_user.to_dict(True)), 200

@auth_bp.route('/profile', methods=['PUT'])
@auth_required('token')
def update_profile():
    data = request.get_json() or {}
    name = str(data.get('name', '')).strip()

    if not name:
        return jsonify({'message': 'Name is required'}), 400

    current_user.name = name
    current_user.bio = str(data.get('bio', '')).strip()
    current_user.interests = str(data.get('interests', '')).strip()
    current_user.profile_image_url = str(data.get('profile_image_url', '')).strip()
    db.session.commit()

    return jsonify({'message': 'Profile updated', 'user': current_user.to_dict(True)}), 200

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
def public_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = user.to_dict()
    data['offerings'] = [item.to_dict() for item in SkillOffering.query.filter_by(teacher_id=user.id, status='ACTIVE').all()]
    data['reviews'] = [item.to_dict() for item in Review.query.filter_by(reviewee_id=user.id).order_by(Review.created_at.desc()).all()]
    return jsonify(data), 200

@auth_bp.route('/logout', methods=['POST'])
@auth_required('token')
def logout():
    user_datastore.set_token_uniquifier(current_user, uuid4().hex)
    db.session.commit()
    return jsonify({'message': 'Logged out'}), 200
