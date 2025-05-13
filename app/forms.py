from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TelField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from models import User
import re
from wtforms.validators import ValidationError


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Обязательное поле"),
        Email(message="Некорректный email")
    ])

    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=8, message="Пароль должен быть не менее 8 символов")
    ])

    password_confirm = PasswordField('Подтверждение пароля', validators=[
        DataRequired(),
        EqualTo('password', message="Пароли должны совпадать")
    ])

    name = StringField('Ваше имя', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])

    phone = TelField('Телефон', validators=[
        DataRequired()
    ])

    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')

    def validate_phone(form, field):
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not phone_pattern.match(field.data):
            raise ValidationError('Некорректный формат телефона')

    # Добавить валидатор к полю phone
    phone = TelField('Телефон', validators=[
        DataRequired(),
        validate_phone
    ])


class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])
    phone = TelField('Телефон', validators=[
        DataRequired(),
        validate_phone
    ])
    avatar = FileField('Аватар', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения')
    ])
    address = TextAreaField('Адрес', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Сохранить')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('new_password')
    ])
    submit = SubmitField('Изменить пароль')


class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField('Адрес доставки', validators=[
        DataRequired(),
        Length(min=10, max=500)
    ])
    payment_method = SelectField('Способ оплаты', choices=[
        ('card', 'Банковская карта'),
        ('cash', 'Наличные при получении'),
        ('invoice', 'Оплата по счету')
    ], validators=[DataRequired()])
    notes = TextAreaField('Примечания', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Оформить заказ')


from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin:
        abort(403)


# Главная панель
@admin_bp.route('/')
def dashboard():
    stats = {
        'products': Product.query.count(),
        'orders': Order.query.filter_by(status='paid').count(),
        'users': User.query.count(),
        'revenue': db.session.query(db.func.sum(Order.total)).filter_by(status='paid').scalar()
    }
    return render_template('admin/dashboard.html', stats=stats)


# Управление товарами
@admin_bp.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/products/list.html', products=products)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            category_id=form.category.data
        )
        db.session.add(product)
        db.session.commit()
        log_admin_action(f"Created product #{product.id}")
        flash('Товар успешно добавлен', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/new.html', form=form)


# Управление заказами
@admin_bp.route('/orders')
def orders():
    status = request.args.get('status', 'all')
    query = Order.query

    if status != 'all':
        query = query.filter_by(status=status)

    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders/list.html', orders=orders, status=status)


@admin_bp.route('/orders/<int:id>/update-status', methods=['POST'])
def update_order_status(id):
    order = Order.query.get_or_404(id)
    new_status = request.form.get('status')

    if new_status not in ['processing', 'shipped', 'delivered', 'cancelled']:
        abort(400)

    order.status = new_status
    db.session.commit()
    log_admin_action(f"Updated order #{id} status to {new_status}")
    flash('Статус заказа обновлен', 'success')
    return redirect(url_for('admin.orders'))


# Система отзывов
@admin_bp.route('/reviews')
def reviews():
    show = request.args.get('show', 'pending')
    query = Review.query

    if show == 'approved':
        query = query.filter_by(is_approved=True)
    elif show == 'rejected':
        query = query.filter_by(is_approved=False)
    else:
        query = query.filter_by(is_approved=None)

    reviews = query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews/list.html', reviews=reviews, show=show)


# Логи администратора
@admin_bp.route('/logs')
def logs():
    page = request.args.get('page', 1, type=int)
    logs = AdminLog.query.order_by(AdminLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('admin/logs.html', logs=logs)


# Вспомогательные функции
def log_admin_action(action):
    log = AdminLog(
        admin_id=current_user.id,
        action=action,
        target_type=request.endpoint.split('.')[-1],
        target_id=request.view_args.get('id')
    )
    db.session.add(log)
    db.session.commit()
