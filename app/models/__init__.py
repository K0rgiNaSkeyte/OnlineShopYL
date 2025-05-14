from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from .review import Review
from .order import Order, OrderItem
from .log import AdminLog
from .cart import Cart, CartItem
from .user_profile import UserProfile

__all__ = [
    'User',
    'Product',
    'Category',
    'Review',
    'Order',
    'OrderItem',
    "AdminLog",
    'Cart',
    'CartItem',
    'UserProfile'
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
    stock = db.Column(db.Integer, default=0)
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
            
    def serialize(self):
        """Сериализация объекта для API"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'old_price': float(self.old_price) if self.old_price else None,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'image_url': self.image_url,
            'rating': float(self.rating),
            'stock': self.stock,
            'in_stock': self.in_stock,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Category(db.Model):
    """Модель категории товаров"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # Связи
    products = db.relationship('Product', back_populates='category')
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))