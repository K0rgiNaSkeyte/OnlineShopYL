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
    return redirect(url_for('account.profile'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Страница профиля пользователя с возможностью редактирования"""
    # Создаем профиль пользователя, если его еще нет
    if not current_user.profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    form = ProfileForm()
    
    if request.method == 'GET':
        # Заполняем форму текущими данными пользователя
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        if current_user.profile:
            form.address.data = current_user.profile.address
    
    if form.validate_on_submit():
        # Обновляем данные пользователя
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        
        # Обновляем профиль
        if current_user.profile:
            current_user.profile.address = form.address.data
        
        # Сохраняем изменения
        db.session.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('account.profile'))
    
    return render_template('account.html', form=form)

@bp.route('/change-email', methods=['POST'])
@login_required
def change_email():
    """Изменение email пользователя"""
    email = request.form.get('email')
    
    if not email:
        flash('Email не может быть пустым', 'danger')
        return redirect(url_for('account.profile'))
    
    # Проверяем, не занят ли email другим пользователем
    existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        flash('Этот email уже используется', 'danger')
        return redirect(url_for('account.profile'))
    
    current_user.email = email
    db.session.commit()
    flash('Email успешно изменен', 'success')
    return redirect(url_for('account.profile'))

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