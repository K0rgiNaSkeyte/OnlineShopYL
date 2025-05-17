from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models import Product, Order, User, Category, UserProfile, CartItem
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
    
    # Проверяем, есть ли товар в корзинах пользователей
    cart_items = CartItem.query.filter_by(product_id=id).all()
    if cart_items:
        # Удаляем товар из всех корзин
        for item in cart_items:
            db.session.delete(item)
    
    # Проверяем, есть ли товар в заказах
    if product.order_items and len(product.order_items) > 0:
        flash(f'Невозможно удалить товар "{product.name}", так как он присутствует в заказах', 'danger')
        return redirect(url_for('admin.products'))
    
    # Удаляем товар
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


@admin_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_category(id):
    """Редактирование категории"""
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    
    # Добавляем пустой выбор для категорий верхнего уровня
    choices = [(0, 'Нет (категория верхнего уровня)')]
    # Исключаем текущую категорию и ее дочерние категории из списка
    for c in Category.query.filter(Category.id != id).all():
        # Проверяем, что категория не является дочерней для редактируемой
        if not (c.parent_id == id):
            choices.append((c.id, c.name))
    
    form.parent_id.choices = choices
    
    # Устанавливаем значение parent_id для формы
    if category.parent_id:
        form.parent_id.data = category.parent_id
    else:
        form.parent_id.data = 0

    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.parent_id = form.parent_id.data if form.parent_id.data > 0 else None
        
        db.session.commit()
        flash('Категория успешно обновлена', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('category_edit.html', form=form, category=category, title='Редактирование категории')


@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@admin_required
def delete_category(id):
    """Удаление категории"""
    category = Category.query.get_or_404(id)
    
    # Проверяем, есть ли товары в этой категории
    if category.products and len(category.products) > 0:
        flash(f'Невозможно удалить категорию "{category.name}", так как в ней есть товары', 'danger')
        return redirect(url_for('admin.categories'))
    
    # Проверяем, есть ли дочерние категории
    child_categories = Category.query.filter_by(parent_id=id).all()
    if child_categories:
        flash(f'Невозможно удалить категорию "{category.name}", так как у нее есть дочерние категории', 'danger')
        return redirect(url_for('admin.categories'))
    
    # Удаляем категорию
    db.session.delete(category)
    db.session.commit()
    flash('Категория успешно удалена', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/orders')
@admin_required
def orders():
    """Управление заказами"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    status_filter = request.args.get('status')
    search_query = request.args.get('q')
    
    # Базовый запрос
    query = Order.query
    
    # Фильтр по статусу
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    # Поиск по ID заказа
    if search_query and search_query.isdigit():
        query = query.filter(Order.id == int(search_query))
    
    # Сортировка по дате создания (сначала новые)
    query = query.order_by(Order.created_at.desc())
    
    # Пагинация
    pagination = query.paginate(page=page, per_page=per_page)
    orders = pagination.items
    
    # Добавляем статус и цвет для отображения
    for order in orders:
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
    
    return render_template('orders_admin.html', 
                          orders=orders, 
                          pagination=pagination,
                          status_filter=status_filter,
                          search_query=search_query)


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def view_order(order_id):
    """Просмотр заказа"""
    order = Order.query.get_or_404(order_id)
    
    # Извлекаем информацию о способе доставки из адреса
    shipping_method = "Стандартная доставка"
    notes = ""
    
    if order.shipping_address and "Способ доставки:" in order.shipping_address:
        address_parts = order.shipping_address.split("\n\n")
        if len(address_parts) > 1:
            shipping_info = address_parts[1].split("\n")
            for info in shipping_info:
                if info.startswith("Способ доставки:"):
                    shipping_method = info.replace("Способ доставки:", "").strip()
                elif info.startswith("Примечания:"):
                    notes = info.replace("Примечания:", "").strip()
            
            # Очищаем адрес от дополнительной информации
            order.clean_address = address_parts[0]
        else:
            order.clean_address = order.shipping_address
    else:
        order.clean_address = order.shipping_address
    
    # Добавляем информацию к объекту заказа
    order.shipping_method = shipping_method
    order.notes = notes
    
    # Добавляем статус и цвет для отображения
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
    
    return render_template('order_admin_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Изменение статуса заказа"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    # Проверяем, что статус допустимый
    valid_statuses = ['created', 'paid', 'shipped', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        flash('Недопустимый статус заказа', 'danger')
        return redirect(url_for('admin.view_order', order_id=order_id))
    
    # Обновляем статус
    order.status = new_status
    db.session.commit()
    
    # Определяем текст статуса для сообщения
    status_text = {
        'created': 'Создан',
        'paid': 'Оплачен',
        'shipped': 'Отправлен',
        'completed': 'Доставлен',
        'cancelled': 'Отменен'
    }.get(new_status, new_status)
    
    flash(f'Статус заказа №{order_id} изменен на "{status_text}"', 'success')
    return redirect(url_for('admin.view_order', order_id=order_id))


@admin_bp.route('/users')
@admin_required
def users():
    """Управление пользователями"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('q', '')
    
    # Базовый запрос
    query = User.query
    
    # Поиск по email
    if search_query:
        query = query.filter(User.email.ilike(f'%{search_query}%'))
    
    # Фильтр по роли
    role_filter = request.args.get('role')
    if role_filter == 'admin':
        query = query.filter(User.is_admin == True)
    elif role_filter == 'user':
        query = query.filter(User.is_admin == False)
    
    # Пагинация
    pagination = query.paginate(page=page, per_page=per_page)
    users = pagination.items
    
    return render_template('users.html', 
                          users=users, 
                          pagination=pagination,
                          search_query=search_query,
                          role_filter=role_filter)


@admin_bp.route('/users/<int:id>')
@admin_required
def view_user(id):
    """Просмотр профиля пользователя"""
    user = User.query.get_or_404(id)
    return render_template('user_profile.html', user=user)


@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    """Удаление пользователя"""
    user = User.query.get_or_404(id)
    
    # Проверка, что админ не удаляет сам себя
    if user.id == current_user.id:
        flash('Вы не можете удалить свой аккаунт', 'danger')
        return redirect(url_for('admin.users'))
    
    # Проверяем, есть ли у пользователя заказы
    if user.orders and len(user.orders) > 0:
        flash(f'Невозможно удалить пользователя {user.email}, так как у него есть заказы', 'danger')
        return redirect(url_for('admin.users'))
    
    # Удаляем отзывы пользователя
    if hasattr(user, 'reviews'):
        for review in user.reviews:
            db.session.delete(review)
    
    # Удаляем корзину пользователя
    if user.cart:
        # Удаляем все элементы корзины
        for item in user.cart.items:
            db.session.delete(item)
        db.session.delete(user.cart)
    
    # Удаляем профиль пользователя, если он существует
    if user.profile:
        db.session.delete(user.profile)
    
    # Удаляем пользователя
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Пользователь {user.email} успешно удален', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/toggle-admin/<int:id>', methods=['POST'])
@admin_required
def toggle_admin(id):
    """Выдача/отзыв прав администратора"""
    user = User.query.get_or_404(id)
    
    # Проверка, что админ не снимает права с самого себя
    if user.id == current_user.id:
        flash('Вы не можете изменить свои права администратора', 'danger')
        return redirect(url_for('admin.users'))
    
    # Инвертируем статус администратора
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = "выданы" if user.is_admin else "отозваны"
    flash(f'Права администратора {action} для пользователя {user.email}', 'success')
    return redirect(url_for('admin.users'))