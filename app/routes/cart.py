from flask import render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Product, Cart, CartItem
from app.services.cart_service import get_or_create_cart, add_to_cart, get_cart_total
from app import db
from . import main_bp

@main_bp.route('/cart')
@login_required
def cart():
    """Страница корзины"""
    cart = current_user.cart
    cart_data = get_cart_total(cart)
    
    return render_template('cart.html', 
                          cart_items=cart_data['items'],
                          total=cart_data['total'],
                          total_items=cart_data['total_items'],
                          subtotal=cart_data['subtotal'],
                          discount=cart_data['discount'],
                          delivery_cost=cart_data['delivery_cost'])

@main_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart_route():
    """Добавление товара в корзину"""
    if request.is_json:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
    else:
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', 1, type=int)
    
    if not product_id:
        return jsonify({'success': False, 'error': 'Не указан товар'}), 400
        
    try:
        # Добавляем товар в корзину
        cart_item = add_to_cart(current_user.id, product_id, quantity)
        
        # Получаем обновленное количество товаров в корзине
        cart = current_user.cart
        cart_count = sum(item.quantity for item in cart.items) if cart and cart.items else 0
        
        if request.is_json:
            return jsonify({
                'success': True, 
                'message': 'Товар добавлен в корзину',
                'cart_count': cart_count
            })
        
        flash('Товар добавлен в корзину', 'success')
        return redirect(url_for('main.cart'))
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'Ошибка при добавлении товара в корзину: {str(e)}', 'danger')
        return redirect(url_for('main.catalog'))

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
    
    # Получаем обновленное количество товаров в корзине
    cart = current_user.cart
    cart_count = sum(item.quantity for item in cart.items) if cart and cart.items else 0
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'cart_count': cart_count})
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
    
    # Получаем обновленное количество товаров в корзине
    cart = current_user.cart
    cart_count = sum(item.quantity for item in cart.items) if cart and cart.items else 0
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'cart_count': cart_count})
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
        return jsonify({'success': True, 'cart_count': 0})
    return redirect(url_for('main.cart'))