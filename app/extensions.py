from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_assets import Environment
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
assets = Environment()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


# Настройка требований к паролю
def check_password_complexity(password):
    """
    Проверка сложности пароля:
    - Минимум 8 символов
    - Хотя бы 1 цифра
    - Хотя бы 1 спецсимвол
    """
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(not char.isalnum() for char in password):
        return False
    return True


def send_confirmation_email(user):
    from flask import current_app
    from flask_mail import Message

    msg = Message(
        'Подтверждение регистрации',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email]
    )
    msg.body = f"""
    Для завершения регистрации перейдите по ссылке:
    {url_for('auth.confirm_email', token=generate_confirmation_token(user.email), _external=True)}
    """
    mail.send(msg)
