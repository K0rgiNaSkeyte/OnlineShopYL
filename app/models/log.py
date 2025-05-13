from datetime import datetime
from app import db


class AdminLog(db.Model):
    """Лог действий администратора"""
    __tablename__ = 'admin_logs'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # Например: "updated product 123"
    entity_type = db.Column(db.String(50))  # product, order, user
    entity_id = db.Column(db.Integer)  # ID сущности
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship('User', foreign_keys=[admin_id])


class UserActionLog(db.Model):
    """Лог действий пользователей"""
    __tablename__ = 'user_action_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)