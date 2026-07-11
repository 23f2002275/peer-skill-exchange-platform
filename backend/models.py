from datetime import datetime
from flask_security import UserMixin, RoleMixin
from extensions import db

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    interests = db.Column(db.String(255))
    profile_image_url = db.Column(db.String(255))
    credit_balance = db.Column(db.Integer, default=3)
    average_rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    offerings = db.relationship('SkillOffering', backref='teacher', lazy=True)
    learning_requests = db.relationship('SessionRequest', backref='learner', lazy=True)

    def to_dict(self, private=False):
        data = {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'interests': self.interests,
            'profile_image_url': self.profile_image_url,
            'average_rating': round(self.average_rating or 0, 2),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if private:
            data['email'] = self.email
            data['credit_balance'] = self.credit_balance
            data['active'] = self.active
            data['roles'] = [role.name for role in self.roles]
        return data

class SkillCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    skills = db.relationship('Skill', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'active': self.active
        }

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_category.id'), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    offerings = db.relationship('SkillOffering', backref='skill', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'name': self.name,
            'description': self.description,
            'active': self.active
        }

class SkillOffering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    proficiency_level = db.Column(db.String(40), nullable=False)
    teaching_mode = db.Column(db.String(40), nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    availability_text = db.Column(db.String(255))
    credit_cost = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    requests = db.relationship('SessionRequest', backref='offering', lazy=True)

    def to_dict(self, details=False):
        data = {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else None,
            'teacher_rating': round(self.teacher.average_rating or 0, 2) if self.teacher else 0,
            'skill_id': self.skill_id,
            'skill_name': self.skill.name if self.skill else None,
            'category_name': self.skill.category.name if self.skill and self.skill.category else None,
            'title': self.title,
            'proficiency_level': self.proficiency_level,
            'teaching_mode': self.teaching_mode,
            'duration_minutes': self.duration_minutes,
            'credit_cost': self.credit_cost,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if details:
            data['description'] = self.description
            data['availability_text'] = self.availability_text
            data['teacher'] = self.teacher.to_dict() if self.teacher else None
            data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data

class SessionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    offering_id = db.Column(db.Integer, db.ForeignKey('skill_offering.id'), nullable=False)
    learner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text)
    preferred_time = db.Column(db.DateTime)
    status = db.Column(db.String(40), default='PENDING')
    credit_reserved = db.Column(db.Boolean, default=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime)
    session = db.relationship('Session', backref='request', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'offering_id': self.offering_id,
            'offering_title': self.offering.title if self.offering else None,
            'skill_name': self.offering.skill.name if self.offering and self.offering.skill else None,
            'teacher_id': self.offering.teacher_id if self.offering else None,
            'teacher_name': self.offering.teacher.name if self.offering and self.offering.teacher else None,
            'learner_id': self.learner_id,
            'learner_name': self.learner.name if self.learner else None,
            'message': self.message,
            'preferred_time': self.preferred_time.isoformat() if self.preferred_time else None,
            'status': self.status,
            'credit_reserved': self.credit_reserved,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'session_id': self.session.id if self.session else None
        }

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('session_request.id'), unique=True, nullable=False)
    scheduled_start = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    meeting_details = db.Column(db.String(255))
    status = db.Column(db.String(40), default='SCHEDULED')
    teacher_confirmed = db.Column(db.Boolean, default=False)
    learner_confirmed = db.Column(db.Boolean, default=False)
    settled = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    reviews = db.relationship('Review', backref='session', lazy=True)

    def to_dict(self, private=False):
        data = {
            'id': self.id,
            'request_id': self.request_id,
            'offering_id': self.request.offering_id if self.request else None,
            'offering_title': self.request.offering.title if self.request and self.request.offering else None,
            'skill_name': self.request.offering.skill.name if self.request and self.request.offering and self.request.offering.skill else None,
            'teacher_id': self.request.offering.teacher_id if self.request and self.request.offering else None,
            'teacher_name': self.request.offering.teacher.name if self.request and self.request.offering and self.request.offering.teacher else None,
            'learner_id': self.request.learner_id if self.request else None,
            'learner_name': self.request.learner.name if self.request and self.request.learner else None,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'teacher_confirmed': self.teacher_confirmed,
            'learner_confirmed': self.learner_confirmed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reviewed_by': [review.reviewer_id for review in self.reviews]
        }
        if private:
            data['meeting_details'] = self.meeting_details
        return data

class CreditTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(40), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', foreign_keys=[user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    reviewee = db.relationship('User', foreign_keys=[reviewee_id])
    __table_args__ = (db.UniqueConstraint('session_id', 'reviewer_id', name='unique_session_reviewer'),)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'reviewee_id': self.reviewee_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    offering_id = db.Column(db.Integer, db.ForeignKey('skill_offering.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    reason = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text)
    status = db.Column(db.String(30), default='OPEN')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reporter = db.relationship('User', foreign_keys=[reporter_id])

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'reporter_name': self.reporter.name if self.reporter else None,
            'reported_user_id': self.reported_user_id,
            'offering_id': self.offering_id,
            'session_id': self.session_id,
            'reason': self.reason,
            'details': self.details,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
