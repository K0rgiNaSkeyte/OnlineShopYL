from app import db
from datetime import datetime


class Cart(db.Model):
    """Модель корзины пользователя"""
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Связи
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def get_total(self):
        """Расчет общей суммы корзины"""
        return sum(item.product.price * item.quantity for item in self.items)


class CartItem(db.Model):
    """Элемент корзины"""
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def increase(self, amount=1):
        """Увеличение количества"""
        self.quantity += amount
        db.session.commit()

    def decrease(self, amount=1):
        """Уменьшение количества"""
        if self.quantity > amount:
            self.quantity -= amount
        else:
            db.session.delete(self)
        db.session.commit()
