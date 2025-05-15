from flask import render_template, request, abort, Blueprint, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import Product, Category, Review
from app import db
from sqlalchemy.exc import IntegrityError
from . import main_bp

@main_bp.route('/catalog')
def catalog():
    """Страница каталога товаров"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category')

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.paginate(page=page, per_page=12)
    categories = Category.query.all()
    return render_template('catalog.html',
                           products=products,
                           categories=categories)


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
    
    return render_template('product.html', 
                          product=product, 
                          user_review=user_review,
                          reviews=approved_reviews)


@main_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Добавление отзыва к товару"""
    product = Product.query.get_or_404(product_id)
    
    rating = request.form.get('rating', type=int)
    text = request.form.get('text')
    
    if not rating or rating < 1 or rating > 5:
        flash('Пожалуйста, укажите оценку от 1 до 5', 'danger')
        return redirect(url_for('main_bp.product_detail', id=product_id))
    
    # Проверяем, есть ли уже отзыв от этого пользователя
    existing_review = Review.query.filter_by(
        product_id=product_id,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        flash('Вы уже оставили отзыв на этот товар', 'warning')
        return redirect(url_for('main_bp.product_detail', id=product_id))
    
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
    
    return redirect(url_for('main_bp.product_detail', id=product_id))