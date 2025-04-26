from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from pathlib import Path

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    # Создание экземпляра Flask
    app = Flask(__name__,
                template_folder=str(Path(__file__).parent / 'frontend' / 'templates'),
                static_folder=str(Path(__file__).parent / 'frontend' / 'static'))

    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(Path(__file__).parent / 'db.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = str(Path(__file__).parent / 'frontend' / 'static' / 'images' / 'products')

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Настройка Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
    login_manager.login_message_category = 'warning'

    # Регистрация Blueprints
    from backend.auth import auth_bp
    from backend.products import products_bp
    from backend.cart import cart_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')

    # CLI команды
    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        print('База данных инициализирована')

    @app.cli.command('create-admin')
    def create_admin():
        from backend.models import User
        admin = User(
            email='admin@example.com',
            name='Admin',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Администратор создан')

    return app


if __name__ == '__main__':
    app = create_app()

    # Перед запуском выводим информацию о путях
    print(f"Шаблоны: {app.template_folder}")
    print(f"Статика: {app.static_folder}")
    print(f"База данных: {app.config['SQLALCHEMY_DATABASE_URI']}")

    app.run(debug=True)
