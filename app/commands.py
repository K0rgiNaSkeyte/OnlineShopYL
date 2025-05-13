import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User, Product, Category, Review, Order, OrderItem
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def register_commands(app):
    """Регистрация CLI-команд"""

    @app.cli.command('init-db')
    @click.confirmation_option(prompt='Вы уверены? Это удалит все данные!')
    @with_appcontext
    def init_db():
        """Инициализация БД с тестовыми данными"""
        # Удаление и создание таблиц
        db.drop_all()
        db.create_all()

        # Создание тестовых данных
        admin = User(
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            name='Admin',
            phone='+79001234567',
            is_admin=True
        )

        user = User(
            email='user@example.com',
            password_hash=generate_password_hash('user123'),
            name='Иван Иванов',
            phone='+79007654321'
        )

        # Категории
        categories = [
            Category(name='Электроника', slug='electronics'),
            Category(name='Книги', slug='books')
        ]

        # Товары
        products = [
            Product(
                name='Смартфон X',
                price=79990,
                old_price=89990,
                description='Флагманский смартфон',
                category=categories[0],
                image_url='/static/images/phone.jpg'
            ),
            Product(
                name='Ноутбук Pro',
                price=129990,
                description='Мощный ноутбук для работы',
                category=categories[0],
                image_url='/static/images/laptop.jpg'
            ),
            Product(
                name='Книга по Python',
                price=2490,
                description='Изучение Python для начинающих',
                category=categories[1],
                image_url='/static/images/book.jpg'
            )
        ]

        # Отзывы
        reviews = [
            Review(
                product=products[0],
                user=user,
                rating=5,
                text='Отличный телефон!',
                is_approved=True
            )
        ]

        # Заказы
        order = Order(
            user=user,
            total_price=79990,
            status='delivered',
            payment_method='credit_card',
            shipping_address='г. Москва, ул. Примерная, 1',
            created_at=datetime.utcnow() - timedelta(days=3)
        )

        order_item = OrderItem(
            order=order,
            product=products[0],
            quantity=1,
            price=79990
        )

        # Сохранение всех данных
        db.session.add_all([admin, user] + categories + products + reviews)
        db.session.add(order)
        db.session.add(order_item)
        db.session.commit()

        click.echo('База данных инициализирована с тестовыми данными')
