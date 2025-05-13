from flask import render_template
from . import main_bp
from flask import Blueprint

bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Главная страница"""
    return render_template('main/index.html')


@main_bp.route('/about')
def about():
    """Страница 'О нас'"""
    return render_template('main/about.html')


@main_bp.route('/contacts')
def contacts():
    """Страница контактов"""
    return render_template('main/contacts.html')
