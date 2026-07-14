from uuid import uuid4
import pytest
from flask_security import hash_password
from app import create_app
from extensions import db
from security_setup import user_datastore
from models import SkillCategory, Skill, SkillOffering, CreditTransaction

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite://',
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        db.create_all()
        user_datastore.create_role(name='admin')
        user_datastore.create_role(name='member')

        teacher = user_datastore.create_user(
            email='teacher@test.com',
            name='Teacher',
            password=hash_password('password'),
            roles=['member'],
            credit_balance=3,
            fs_uniquifier=uuid4().hex,
        )
        learner = user_datastore.create_user(
            email='learner@test.com',
            name='Learner',
            password=hash_password('password'),
            roles=['member'],
            credit_balance=3,
            fs_uniquifier=uuid4().hex,
        )
        category = SkillCategory(name='Programming')
        db.session.add(category)
        db.session.flush()
        skill = Skill(category_id=category.id, name='Python')
        db.session.add(skill)
        db.session.flush()
        offering = SkillOffering(
            teacher_id=teacher.id,
            skill_id=skill.id,
            title='Python help',
            proficiency_level='Beginner',
            teaching_mode='Online',
            duration_minutes=60,
            credit_cost=1
        )
        db.session.add(offering)
        db.session.add_all([
            CreditTransaction(user_id=teacher.id, amount=3, transaction_type='STARTER', reason='Starter credits'),
            CreditTransaction(user_id=learner.id, amount=3, transaction_type='STARTER', reason='Starter credits')
        ])
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, email):
    response = client.post('/api/auth/login', json={'email': email, 'password': 'password'})
    return response.get_json()['token']

def test_invalid_login(client):
    response = client.post('/api/auth/login', json={'email': 'teacher@test.com', 'password': 'wrong'})
    assert response.status_code == 401

def test_member_can_create_offering(client):
    token = login(client, 'learner@test.com')
    response = client.post('/api/offerings', headers={'Authentication-Token': token}, json={
        'skill_id': 1,
        'title': 'Python practice',
        'proficiency_level': 'Beginner',
        'teaching_mode': 'Online',
        'duration_minutes': 45,
        'credit_cost': 1
    })
    assert response.status_code == 201

def test_user_cannot_request_own_offering(client):
    token = login(client, 'teacher@test.com')
    response = client.post('/api/offerings/1/requests', headers={'Authentication-Token': token}, json={})
    assert response.status_code == 400

def test_accept_request_reserves_credit(client):
    learner_token = login(client, 'learner@test.com')
    response = client.post('/api/offerings/1/requests', headers={'Authentication-Token': learner_token}, json={
        'message': 'I want to learn'
    })
    request_id = response.get_json()['request']['id']

    teacher_token = login(client, 'teacher@test.com')
    response = client.patch('/api/requests/' + str(request_id) + '/accept', headers={'Authentication-Token': teacher_token})
    assert response.status_code == 200

    response = client.get('/api/credits/transactions', headers={'Authentication-Token': learner_token})
    assert response.get_json()['balance'] == 2
