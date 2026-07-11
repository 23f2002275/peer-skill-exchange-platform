from uuid import uuid4
from flask_security import hash_password
from app import create_app
from extensions import db
from security_setup import user_datastore
from models import SkillCategory, Skill, SkillOffering, CreditTransaction

app = create_app()

with app.app_context():
    db.create_all()

    for role_name in ['admin', 'member']:
        if not user_datastore.find_role(role_name):
            user_datastore.create_role(name=role_name)

    users = [
        ('admin@skillexchange.com', 'Admin User', ['admin'], 'admin123'),
        ('teacher@skillexchange.com', 'Demo Teacher', ['member'], 'teacher123'),
        ('learner@skillexchange.com', 'Demo Learner', ['member'], 'learner123')
    ]

    for email, name, roles, password in users:
        if not user_datastore.find_user(email=email):
            user = user_datastore.create_user(
                email=email,
                name=name,
                password=hash_password(password),
                roles=roles,
                credit_balance=3,
                bio='Student interested in practical peer learning.',
                interests='Programming, design, communication',
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

    category_data = [
        ('Programming', 'Programming languages and software development'),
        ('Design', 'Visual and product design skills'),
        ('Communication', 'Speaking, writing and presentation skills')
    ]

    for name, description in category_data:
        if not SkillCategory.query.filter_by(name=name).first():
            db.session.add(SkillCategory(name=name, description=description))

    db.session.commit()

    skills_data = [
        ('Programming', 'Python', 'Python basics, automation and APIs'),
        ('Programming', 'VueJS', 'Frontend development with VueJS'),
        ('Design', 'Figma', 'Interface design and prototyping'),
        ('Communication', 'Public Speaking', 'Presentation and speaking practice')
    ]

    for category_name, name, description in skills_data:
        if not Skill.query.filter_by(name=name).first():
            category = SkillCategory.query.filter_by(name=category_name).first()
            db.session.add(Skill(category_id=category.id, name=name, description=description))

    db.session.commit()

    teacher = user_datastore.find_user(email='teacher@skillexchange.com')
    python_skill = Skill.query.filter_by(name='Python').first()
    vue_skill = Skill.query.filter_by(name='VueJS').first()

    if SkillOffering.query.count() == 0:
        db.session.add_all([
            SkillOffering(
                teacher_id=teacher.id,
                skill_id=python_skill.id,
                title='Python fundamentals for beginners',
                description='A practical session covering variables, conditions, loops and functions.',
                proficiency_level='Beginner',
                teaching_mode='Online',
                duration_minutes=60,
                availability_text='Weekdays after 7 PM',
                credit_cost=1,
                status='ACTIVE'
            ),
            SkillOffering(
                teacher_id=teacher.id,
                skill_id=vue_skill.id,
                title='Build your first VueJS page',
                description='Learn components, data binding and API calls through a small page.',
                proficiency_level='Intermediate',
                teaching_mode='Online',
                duration_minutes=90,
                availability_text='Saturday afternoon',
                credit_cost=2,
                status='ACTIVE'
            )
        ])
        db.session.commit()

    print('Database created')
    print('admin@skillexchange.com / admin123')
    print('teacher@skillexchange.com / teacher123')
    print('learner@skillexchange.com / learner123')
