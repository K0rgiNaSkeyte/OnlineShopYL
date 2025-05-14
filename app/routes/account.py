from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, UserProfile, Order
from app.forms import ProfileForm, ChangePasswordForm
from app import db
import os

bp = Blueprint('account', __name__, url_prefix='/account')

@bp.route('/')
@login_required
def index():
    """Главная страница личного кабинета"""
    return render_template('account.html')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Страница профиля пользователя"""
    # Просто отображаем профиль без возможности редактирования
    return render_template('account.html')

@bp.route('/orders')
@login_required
def orders():
    """Страница заказов пользователя"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id) \
        .order_by(Order.created_at.desc()) \
        .paginate(page=page, per_page=10)
    return render_template('orders.html', orders=orders)

@bp.route('/orders/<int:order_id>')
@login_required
def order_details(order_id):
    """Страница деталей заказа"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('order.html', order=order)