from flask import Flask
from app.extensions import db, migrate, login_manager
import os

def create_app(config_name=None):
    app = Flask(__name__, 
                template_folder=os.path.join('template'),
                static_folder=os.path.join('static'))
    
    # Загрузка конфигурации из config.py
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')
    
    if isinstance(config_name, str):
        from config import config
        config_class = config.get(config_name, config['default'])
        app.config.from_object(config_class)
    else:
        # Если передан объект конфигурации напрямую
        app.config.from_object(config_name)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Настройка login_manager
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'

    # Контекстные процессоры
    from app.context_processors import cart_processor
    app.context_processor(cart_processor)

    # Регистрация blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # CLI команды
    from app.commands import register_commands
    register_commands(app)

    return app