from flask import Blueprint

# Главные роутеры
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Импорт всех роутов
from . import main, auth, products, orders, cart, admin, account

def register_blueprints(app):
    """Регистрация всех роутов в приложении"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    # Регистрация API ресурсов
    from app.api.routes import register_api_resources
    register_api_resources()