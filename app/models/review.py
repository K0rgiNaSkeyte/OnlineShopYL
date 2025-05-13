from datetime import datetime
from app import db


class Review(db.Model):
    """Модель отзыва о товаре"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=None)  # None - на модерации, True/False

    product = db.relationship('Product', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_bounds'),
    )

    def approve(self):
        """Одобрение отзыва"""
        self.is_approved = True
        db.session.commit()
        self.product.update_rating()

    def reject(self):
        """Отклонение отзыва"""
        self.is_approved = False
        db.session.commit()
