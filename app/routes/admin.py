from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.decorators import admin_required
from app.models import Product, Order, User, Category
from app.forms import ProductForm, CategoryForm
from app import db
from . import admin_bp

@admin_bp.route('/')
@admin_required
def dashboard():
    """Админ-панель"""
    stats = {
        'products': Product.query.count(),
        'orders': Order.query.count(),
        'users': User.query.count()
    }
    return render_template('dashboard.html', stats=stats)

@admin_bp.route('/products')
@admin_required
def products():
    """Управление товарами"""
    products = Product.query.all()
    return render_template('products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Добавление товара"""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category_id=form.category_id.data,
            stock=form.stock.data,
            image=form.image.data if form.image.data else None
        )
        db.session.add(product)
        db.session.commit()
        flash('Товар успешно добавлен', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('product_edit.html', form=form, title='Добавление товара')

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
        if form.image.data:
            product.image = form.image.data
            
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