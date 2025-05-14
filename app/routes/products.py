from flask import render_template, request, abort, Blueprint
from flask_login import login_required, current_user
from app.models import Product, Category
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
    return render_template('product.html', product=product)