from app import db
from datetime import datetime


class UserProfile(db.Model):
    """Модель профиля пользователя с дополнительной информацией"""
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    avatar = db.Column(db.String(255))
    address = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с пользователем
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
