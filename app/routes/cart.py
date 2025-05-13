from flask import jsonify, request
from flask_login import login_required, current_user
from app.models import Cart, CartItem, Product
from . import api_bp


@api_bp.route('/cart', methods=['GET'])
@login_required
def get_cart():
    """Получение содержимого корзины"""
    cart = current_user.cart
    if not cart:
        return jsonify({'items': [], 'total': 0})

    items = [{
        'id': item.id,
        'product_id': item.product_id,
        'name': item.product.name,
        'price': float(item.product.price),
        'quantity': item.quantity
    } for item in cart.items]

    return jsonify({
        'items': items,
        'total': sum(item['price'] * item['quantity'] for item in items)
    })


@api_bp.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Добавление товара в корзину"""
    data = request.get_json()
    product = Product.query.get_or_404(data['product_id'])

    # Логика добавления в корзину
    return jsonify({'success': True})
