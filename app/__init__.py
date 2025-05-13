from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистрация blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.products import bp as products_bp
    from app.routes.orders import bp as orders_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.account import bp as account_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(account_bp)

    # CLI команды
    from app.commands import register_commands
    register_commands(app)

    return app