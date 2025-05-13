from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from .review import Review
from .order import Order, OrderItem
from .log import AdminLog
from .cart import Cart, CartItem

__all__ = [
    'User',
    'Product',
    'Category',
    'Review',
    'Order',
    'OrderItem',
    "AdminLog",
    'Cart',
    'CartItem'
]


class User(UserMixin, db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Связи
    orders = db.relationship('Order', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')
    cart = db.relationship('Cart', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    """Модель товара"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_url = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    in_stock = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    reviews = db.relationship('Review', back_populates='product', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='product')
    cart_items = db.relationship('CartItem', back_populates='product')
    category = db.relationship('Category', back_populates='products')

    def update_rating(self):
        """Пересчет рейтинга на основе отзывов"""
        if self.reviews:
            self.rating = sum(r.rating for r in self.reviews) / len(self.reviews)
            db.session.commit()


class Category(db.Model):
    """Модель категории товаров"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True)
    products = db.relationship('Product', back_populates='category')
