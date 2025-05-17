from flask import render_template, request, abort, Blueprint, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Product, Category, Review
from app import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_, func
from . import main_bp

@main_bp.route('/catalog')
def catalog():
    """Страница каталога товаров"""
    # Получаем параметры фильтрации из запроса
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'popular')
    search_query = request.args.get('q')
    in_stock = request.args.get('in_stock')
    
    # Базовый запрос
    query = Product.query
    
    # Фильтр по категории
    if category_id:
        category = Category.query.get(category_id)
        if category:
            # Получаем ID всех подкатегорий
            category_ids = [category.id]
            for child in Category.query.filter_by(parent_id=category.id).all():
                category_ids.append(child.id)
            query = query.filter(Product.category_id.in_(category_ids))
    
    # Фильтр по цене
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Фильтр по наличию
    if in_stock == 'true':
        query = query.filter(Product.in_stock == True)
    elif in_stock == 'false':
        query = query.filter(Product.in_stock == False)
    
    # Поиск по названию и описанию
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    # Сортировка
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:  # По умолчанию по популярности (рейтингу)
        query = query.order_by(Product.rating.desc())
    
    # Пагинация результатов
    products = query.paginate(page=page, per_page=12)
    
    # Получаем все категории для фильтра
    categories = Category.query.all()
    
    # Подготавливаем категории с количеством товаров
    category_counts = {}
    for cat in categories:
        category_counts[cat.id] = Product.query.filter_by(category_id=cat.id).count()
    
    # Определяем минимальную и максимальную цену для фильтра
    min_product_price = db.session.query(func.min(Product.price)).scalar() or 0
    max_product_price = db.session.query(func.max(Product.price)).scalar() or 10000
    
    return render_template('catalog.html',
                          products=products,
                          categories=categories,
                          category_counts=category_counts,
                          min_product_price=min_product_price,
                          max_product_price=max_product_price,
                          current_filters={
                              'category_id': category_id,
                              'min_price': min_price or min_product_price,
                              'max_price': max_price or max_product_price,
                              'sort_by': sort_by,
                              'search_query': search_query,
                              'in_stock': in_stock
                          })


@main_bp.route('/product/<int:id>')
def product_detail(id):
    """Страница товара"""
    product = Product.query.get_or_404(id)
    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            product_id=id, 
            user_id=current_user.id
        ).first()
    
    approved_reviews = Review.query.filter_by(
        product_id=id, 
        is_approved=True
    ).order_by(Review.created_at.desc()).all()
    
    # Получаем похожие товары из той же категории
    similar_products = []
    if product.category_id:
        similar_products = Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id
        ).order_by(Product.rating.desc()).limit(4).all()
    
    return render_template('product.html', 
                          product=product, 
                          user_review=user_review,
                          reviews=approved_reviews,
                          similar_products=similar_products)


@main_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Добавление отзыва к товару"""
    product = Product.query.get_or_404(product_id)
    
    rating = request.form.get('rating', type=int)
    text = request.form.get('text')
    
    if not rating or rating < 1 or rating > 5:
        flash('Пожалуйста, укажите оценку от 1 до 5', 'danger')
        return redirect(url_for('main.product_detail', id=product_id))
    
    # Проверяем, есть ли уже отзыв от этого пользователя
    existing_review = Review.query.filter_by(
        product_id=product_id,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        flash('Вы уже оставили отзыв на этот товар', 'warning')
        return redirect(url_for('main.product_detail', id=product_id))
    
    try:
        review = Review(
            product_id=product_id,
            user_id=current_user.id,
            rating=rating,
            text=text,
            is_approved=None  # На модерации
        )
        
        db.session.add(review)
        db.session.commit()
        flash('Спасибо! Ваш отзыв отправлен на модерацию', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Вы уже оставили отзыв на этот товар', 'warning')
    
    return redirect(url_for('main.product_detail', id=product_id))


@main_bp.route('/search')
def search():
    """Поиск товаров"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.catalog'))
    
    return redirect(url_for('main.catalog', q=query))