from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models import Product, Order, User
from . import admin_bp

bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_required
def dashboard():
    """Админ-панель"""
    stats = {
        'products': Product.query.count(),
        'orders': Order.query.count(),
        'users': User.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/products')
@admin_required
def manage_products():
    """Управление товарами"""
    products = Product.query.all()
    return render_template('admin/products/list.html', products=products)
