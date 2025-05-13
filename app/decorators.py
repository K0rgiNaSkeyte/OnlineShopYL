from functools import wraps
from flask import abort, request
from flask_login import current_user
from app.models import User


def profile_owner_required(f):
    @wraps(f)
    def decorated_function(user_id, *args, **kwargs):
        if not current_user.is_admin and current_user.id != user_id:
            abort(403)
        return f(user_id, *args, **kwargs)

    return decorated_function


def admin_required(f):
    """Декоратор для проверки прав администратора"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def json_required(f):
    """Требует JSON-запрос"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            abort(400, description="Request must be JSON")
        return f(*args, **kwargs)

    return decorated_function


def log_action(action_description):
    """Логирование действий пользователя"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            if current_user.is_authenticated:
                log = UserActionLog(
                    user_id=current_user.id,
                    action=action_description,
                    endpoint=request.endpoint,
                    ip_address=request.remote_addr
                )
                db.session.add(log)
                db.session.commit()
            return result

        return decorated_function

    return decorator
