from datetime import datetime
from app import db


class Payment(db.Model):
    """Модель платежа"""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50))  # card, apple_pay, etc.
    status = db.Column(db.String(20), default='pending')  # pending, succeeded, failed
    transaction_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', back_populates='payments')

    def mark_as_paid(self, transaction_id):
        """Отметка платежа как успешного"""
        self.status = 'succeeded'
        self.transaction_id = transaction_id
        self.order.status = 'paid'
        db.session.commit()
