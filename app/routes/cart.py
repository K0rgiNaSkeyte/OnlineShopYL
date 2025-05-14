from flask import render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Product, Cart, CartItem
from app import db
from . import main_bp

@main_bp.route('/cart')
@login_required
def cart():
    """Страница корзины"""
    cart = current_user.cart
    cart_items = []
    total = 0
    total_items = 0
    discount = 0
    delivery_cost = 0
    
    if cart and cart.items:
        cart_items = cart.items
        total_items = sum(item.quantity for item in cart_items)
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        # Здесь можно добавить логику расчета скидки
        total = subtotal - discount + delivery_cost
    
    return render_template('cart.html', 
                          cart_items=cart_items,
                          total=total,
                          total_items=total_items,
                          subtotal=subtotal if 'subtotal' in locals() else 0,
                          discount=discount,
                          delivery_cost=delivery_cost)

@main_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Добавление товара в корзину"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    if not product_id:
        return jsonify({'success': False, 'error': 'Не указан товар'}), 400
        
    product = Product.query.get_or_404(product_id)
    
    # Получаем или создаем корзину для пользователя
    cart = current_user.cart
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    # Проверяем, есть ли уже такой товар в корзине
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if cart_item:
        # Если товар уже в корзине, увеличиваем количество
        cart_item.quantity += quantity
    else:
        # Иначе добавляем новый товар
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Товар добавлен в корзину', 'success')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect(url_for('main.cart'))

@main_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    """Обновление количества товара в корзине"""
    item_id = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if not item_id or not quantity:
        return jsonify({'success': False, 'error': 'Неверные параметры'}), 400
    
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Проверяем, принадлежит ли товар корзине текущего пользователя
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Доступ запрещен'}), 403
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect(url_for('main.cart'))

@main_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Удаление товара из корзины"""
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Проверяем, принадлежит ли товар корзине текущего пользователя
    if cart_item.cart.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Доступ запрещен'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect(url_for('main.cart'))

@main_bp.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    """Очистка корзины"""
    cart = current_user.cart
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect(url_for('main.cart'))