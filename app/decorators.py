from functools import wraps
from flask import abort
from flask_login import current_user


def profile_owner_required(f):
    @wraps(f)
    def decorated_function(user_id, *args, **kwargs):
        if not current_user.is_admin and current_user.id != user_id:
            abort(403)
        return f(user_id, *args, **kwargs)

    return decorated_function
