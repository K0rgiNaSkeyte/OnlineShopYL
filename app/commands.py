import click
from app.extensions import db
from models import User, Product, Category, Review, Order, OrderItem
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def init_db_cli(app):
    @app.cli.command('init-db')
    @click.confirmation_option(prompt='Вы уверены? Это удалит все данные!')
    def init_db():
        """Инициализация БД с тестовыми данными"""
        db.drop_all()
        db.create_all()

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

        electronics = Category(name='Электроника', slug='electronics')
        books = Category(name='Книги', slug='books')

        products = [
            Product(
                name='Смартфон X',
                price=79990,
                old_price=89990,
                description='Флагманский смартфон',
                category=electronics,
                image_url='/static/images/phone.jpg'
            ),
            Product(
                name='Ноутбук Pro',
                price=129990,
                description='Мощный ноутбук для работы',
                category=electronics,
                image_url='/static/images/laptop.jpg'
            ),
            Product(
                name='Книга по Python',
                price=2490,
                description='Изучение Python для начинающих',
                category=books,
                image_url='/static/images/book.jpg'
            )
        ]

        reviews = [
            Review(
                product=products[0],
                user=user,
                rating=5,
                text='Отличный телефон!',
                is_approved=True
            )
        ]

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

        db.session.add_all([admin, user, electronics, books] + products + reviews)
        db.session.add(order)
        db.session.add(order_item)

        db.session.commit()
        click.echo('База данных инициализирована с тестовыми данными')

    return init_db
