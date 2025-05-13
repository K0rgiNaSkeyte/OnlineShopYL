from datetime import datetime
from app import db


class Order(db.Model):
    """Модель заказа"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='created')  # created, paid, shipped, completed, cancelled
    payment_method = db.Column(db.String(50))
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Связи
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def cancel(self):
        """Отмена заказа"""
        if self.status not in ('completed', 'cancelled'):
            self.status = 'cancelled'
            db.session.commit()


class OrderItem(db.Model):
    """Элемент заказа"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Фиксированная цена на момент заказа

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')
