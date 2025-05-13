from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager
from routes.account import account_bp
from api.account import ProfileAPI, OrdersAPI
from app.routes.admin import admin_bp
from app.api.admin import AdminProductAPI, AdminOrderAPI


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистрация blueprints
    from routes import main, auth, products, orders, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)

    # Обработчики ошибок
    from errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    #API
    api = Api(app)
    api.add_resource(ProfileAPI, '/api/profile')
    api.add_resource(OrdersAPI, '/api/orders')
    api.add_resource(AdminProductAPI, '/api/admin/products/<int:product_id>')
    api.add_resource(AdminOrderAPI, '/api/admin/orders/<int:order_id>')

    # CLI команды
    from commands import init_db_cli
    app.cli.add_command(init_db_cli)

    return app
