import re
from wtforms.validators import ValidationError
from app.models import User


def validate_phone(form, field):
    """Валидатор номера телефона"""
    phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    if not phone_pattern.match(field.data):
        raise ValidationError('Некорректный формат телефона')


def unique_email(form, field):
    """Проверка уникальности email"""
    if User.query.filter_by(email=field.data.lower()).first():
        raise ValidationError('Этот email уже зарегистрирован')


def password_complexity(form, field):
    """Проверка сложности пароля"""
    password = field.data
    if len(password) < 8:
        raise ValidationError('Пароль должен содержать минимум 8 символов')
    if not any(char.isdigit() for char in password):
        raise ValidationError('Пароль должен содержать цифры')
    if not any(char.isupper() for char in password):
        raise ValidationError('Пароль должен содержать заглавные буквы')
