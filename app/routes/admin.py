from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.decorators import admin_required
from app.models import Product, Order, User, Category
from app.forms import ProductForm, CategoryForm
from app import db
from app.routes import admin_bp
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename

@admin_bp.route('/')
@admin_required
def dashboard():
    """Админ-панель"""
    # Базовая статистика
    stats = {
        'products': Product.query.count(),
        'orders': Order.query.count(),
        'users': User.query.count(),
        'revenue': db.session.query(func.sum(Order.total_price)).scalar() or 0
    }

    # Последние заказы
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    # Добавляем статус и цвет для отображения
    for order in recent_orders:
        if order.status == 'created':
            order.status_text = 'Создан'
            order.status_color = 'secondary'
        elif order.status == 'paid':
            order.status_text = 'Оплачен'
            order.status_color = 'primary'
        elif order.status == 'shipped':
            order.status_text = 'Отправлен'
            order.status_color = 'info'
        elif order.status == 'completed':
            order.status_text = 'Доставлен'
            order.status_color = 'success'
        elif order.status == 'cancelled':
            order.status_text = 'Отменен'
            order.status_color = 'danger'
        else:
            order.status_text = order.status
            order.status_color = 'secondary'

    # Популярные товары (заглушка, в реальном приложении нужно реализовать логику)
    popular_products = []

    return render_template('dashboard.html',
                           stats=stats,
                           recent_orders=recent_orders,
                           popular_products=popular_products)


@admin_bp.route('/products')
@admin_required
def products():
    """Управление товарами"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Получаем товары с пагинацией
    pagination = Product.query.paginate(page=page, per_page=per_page)
    products = pagination.items
    
    # Получаем все категории для фильтра
    categories = Category.query.all()
    
    return render_template('products.html', 
                          products=products, 
                          pagination=pagination,
                          categories=categories)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Добавление товара"""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        # Обработка загрузки изображения
        image_url = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_folder = os.path.join('app', 'static', 'uploads', 'products')
            
            # Создаем папку, если она не существует
            os.makedirs(upload_folder, exist_ok=True)
            
            # Сохраняем файл
            file_path = os.path.join(upload_folder, filename)
            form.image.data.save(file_path)
            
            # URL для доступа к изображению
            image_url = f'/static/uploads/products/{filename}'
        
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category_id=form.category_id.data,
            stock=form.stock.data,
            image_url=image_url,
            in_stock=form.stock.data > 0
        )
        db.session.add(product)
        db.session.commit()
        flash('Товар успешно добавлен', 'success')
        return redirect(url_for('admin.products'))

    return render_template('product_edit.html', form=form, title='Добавление товара')


@admin_bp.route('/products/<int:id>')
@admin_required
def view_product(id):
    """Просмотр товара"""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    return render_template('product_edit.html', form=form, product=product, title='Просмотр товара', readonly=True)


@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    """Редактирование товара"""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category_id = form.category_id.data
        product.stock = form.stock.data
        product.in_stock = form.stock.data > 0
        
        # Обработка загрузки изображения
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_folder = os.path.join('app', 'static', 'uploads', 'products')
            
            # Создаем папку, если она не существует
            os.makedirs(upload_folder, exist_ok=True)
            
            # Сохраняем файл
            file_path = os.path.join(upload_folder, filename)
            form.image.data.save(file_path)
            
            # URL для доступа к изображению
            product.image_url = f'/static/uploads/products/{filename}'

        db.session.commit()
        flash('Товар успешно обновлен', 'success')
        return redirect(url_for('admin.products'))

    return render_template('product_edit.html', form=form, product=product, title='Редактирование товара')


@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@admin_required
def delete_product(id):
    """Удаление товара"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Товар успешно удален', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/categories')
@admin_required
def categories():
    """Управление категориями"""
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    """Добавление категории"""
    form = CategoryForm()
    # Добавляем пустой выбор для категорий верхнего уровня
    choices = [(0, 'Нет (категория верхнего уровня)')]
    choices.extend([(c.id, c.name) for c in Category.query.all()])
    form.parent_id.choices = choices

    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data > 0 else None
        )
        db.session.add(category)
        db.session.commit()
        flash('Категория успешно добавлена', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('category_edit.html', form=form, title='Добавление категории')


@admin_bp.route('/orders')
@admin_required
def orders():
    """Управление заказами"""
    orders = Order.query.all()
    return render_template('orders_admin.html', orders=orders)


@admin_bp.route('/users')
@admin_required
def users():
    """Управление пользователями"""
    users = User.query.all()
    return render_template('users.html', users=users)