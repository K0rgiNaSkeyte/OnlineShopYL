from flask import Flask, render_template

app = Flask(__name__)


@app.route("/home")
def about():
    return render_template("index_auth.html")


@app.route('/cart')
def cart():
    return render_template("cart.html")


@app.route('/account')
def account():
    return render_template("account.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/product/test')
def product():
    product_data = {
        'id': 1,
        'name': 'Смартфон Galaxy S23 Ultra',
        'category': 'Смартфоны',
        'category_id': 1,
        'main_image': 'https://via.placeholder.com/600',
        'images': [
            'https://via.placeholder.com/600',
            'https://via.placeholder.com/600/2',
            'https://via.placeholder.com/600/3'
        ],
        'price': 104990,
        'old_price': 119990,
        'discount': 13,
        'rating': 4.7,
        'reviews_count': 42,
        'in_stock': '10+',
        'description': '<p>Флагманский смартфон с лучшей камерой на рынке. 200 Мп основная камера, процессор Snapdragon 8 Gen 2, аккумулятор 5000 мАч.</p>',
        'specifications': [
            {'name': 'Бренд', 'value': 'Samsung'},
            {'name': 'Модель', 'value': 'Galaxy S23 Ultra'},
            {'name': 'Диагональ экрана', 'value': '6.8"'},
            {'name': 'Процессор', 'value': 'Snapdragon 8 Gen 2'},
            {'name': 'Память', 'value': '12/256 ГБ'},
            {'name': 'Камера', 'value': '200 Мп + 12 Мп + 10 Мп'}
        ],
        'reviews': [
            {
                'author': 'Алексей Петров',
                'date': '15.05.2023',
                'rating': 5,
                'text': 'Отличный телефон, камера просто супер!'
            },
            {
                'author': 'Мария Иванова',
                'date': '10.05.2023',
                'rating': 4,
                'text': 'Хороший аппарат, но тяжеловат'
            }
        ]
    }

    return render_template('product.html', product=product_data)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/")
def home_guest():
    return render_template("index.html")


@app.route("/catalog")
def catalog():
    return render_template("catalog.html")


@app.route("/orders")
def orders():
    return render_template("orders.html")


@app.route("/admin/products")
def products():
    return render_template("products.html")


@app.route("/admin")
def dashboard():
    return render_template("dashboard.html")


@app.route('/admin/products/new')
def admin_new_product():
    return render_template('product_edit.html')


@app.route('/admin/products/<int:id>')
def admin_edit_product(id):
    # Mock данные товара
    product = {
        'id': id,
        'name': 'Смартфон Galaxy S23 Ultra',
        'description': 'Флагманский смартфон',
        'full_description': '<p>Подробное описание с <strong>HTML</strong> разметкой</p>',
        'category_id': 1,
        'price': 104990,
        'old_price': 119990,
        'status': 1,
        'rating': 4.7,
        'main_image': 'https://via.placeholder.com/400x300?text=Main+Image',
        'images': [
            'https://via.placeholder.com/400x300?text=Image+1',
            'https://via.placeholder.com/400x300?text=Image+2'
        ],
        'specifications': [
            {'name': 'Экран', 'value': '6.8" AMOLED'},
            {'name': 'Процессор', 'value': 'Snapdragon 8 Gen 2'}
        ]
    }
    return render_template('product_edit.html', product=product)


@app.route('/admin/orders')
def admin_orders():
    return render_template('orders_admin.html')


@app.route('/admin/orders/<int:id>')
def admin_order_detail(id):
    return "Детали заказа #" + str(id)


@app.route('/admin/users')
def admin_users():
    return render_template('users.html')


@app.route('/admin/users/<int:id>')
def admin_user_detail(id):
    return "Профиль пользователя #" + str(id)


if __name__ == '__main__':
    app.run()
