from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TelField, SelectField, TextAreaField, BooleanField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from app.models import db, User, Product, Order, Review, AdminLog
from app import db
import re


# Общая функция валидации телефона для всех форм
def validate_phone(form, field):
    """Кастомный валидатор для международного формата телефона"""
    phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    if not phone_pattern.match(field.data):
        raise ValidationError('Некорректный формат телефона. Используйте международный формат: +71234567890')


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
        DataRequired(),
        validate_phone  # Используем общую функцию валидации
    ])

    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')


class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[
        DataRequired(),
        Length(min=2, max=50)
    ])

    phone = TelField('Телефон', validators=[
        DataRequired(),
        validate_phone  # Используем общую функцию валидации
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
    
    shipping_method = SelectField('Способ доставки', choices=[
        ('standard', 'Стандартная доставка'),
        ('express', 'Экспресс-доставка')
    ], validators=[DataRequired()])

    notes = TextAreaField('Примечания', validators=[
        Optional(),
        Length(max=500)
    ])

    submit = SubmitField('Оформить заказ')


class ProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired()])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    stock = IntegerField('Количество на складе', validators=[DataRequired()])
    image = FileField('Изображение', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Только изображения')
    ])
    submit = SubmitField('Сохранить')


class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Optional()])
    parent_id = SelectField('Родительская категория', coerce=int, validators=[Optional()], default=0)
    submit = SubmitField('Сохранить')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email обязателен"),
        Email(message="Некорректный email")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Введите пароль")
    ])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')