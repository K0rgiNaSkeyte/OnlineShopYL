from flask import jsonify, request
from flask_login import login_required
from app.models import Product
from . import api_bp


@api_bp.route('/products')
def api_products():
    """API для получения товаров"""
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price
    } for p in products])


@api_bp.route('/products/<int:id>')
def api_product_detail(id):
    """API для получения деталей товара"""
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price
    })
