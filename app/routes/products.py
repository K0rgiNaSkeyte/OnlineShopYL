from flask import render_template, request, abort
from flask_login import login_required
from app.models import Product, Category
from . import main_bp


@main_bp.route('/products')
def product_list():
    """Список товаров с фильтрацией"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category')

    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    products = query.paginate(page=page, per_page=12)
    categories = Category.query.all()
    return render_template('products/list.html',
                           products=products,
                           categories=categories)


@main_bp.route('/products/<int:id>')
def product_detail(id):
    """Страница товара"""
    product = Product.query.get_or_404(id)
    return render_template('products/detail.html', product=product)