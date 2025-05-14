from flask import render_template, redirect, url_for
from . import main_bp
from flask_login import current_user

@main_bp.route('/')
def index():
    """Главная страница"""
    if current_user.is_authenticated:
        return render_template('index_auth.html')
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """Страница 'О нас'"""
    return render_template('about.html')


@main_bp.route('/contacts')
def contacts():
    """Страница контактов"""
    return render_template('contacts.html')


# Добавляем маршруты для перенаправления с корневых URL на URL с префиксами
@main_bp.route('/login')
def login_redirect():
    """Перенаправление на страницу входа"""
    return redirect(url_for('auth.login'))


@main_bp.route('/register')
def register_redirect():
    """Перенаправление на страницу регистрации"""
    return redirect(url_for('auth.register'))