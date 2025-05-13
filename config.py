import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Безопасность
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-key-123'
    CSRF_ENABLED = True

    # База данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///shop.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Настройки Flask-Login
    LOGIN_DISABLED = False
    LOGIN_VIEW = 'auth.login'

    # Настройки загрузки файлов
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Почта (если требуется)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # Пагинация
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10

    # Админ-панель
    ADMIN_PANEL_ITEMS_PER_PAGE = 20
    ADMIN_ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}
    ADMIN_UPLOAD_FOLDER = 'static/uploads'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Логирование SQL-запросов


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    PREFERRED_URL_SCHEME = 'https'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
