from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Order, OrderItem
from app.forms import CheckoutForm
from app.services.order_service import create_order_from_cart
from app import db
from . import main_bp

@main_bp.route('/orders')
@login_required
def orders_list():
    """Список заказов пользователя"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id) \
        .order_by(Order.created_at.desc()) \
        .paginate(page=page, per_page=10)
    return render_template('orders.html', orders=orders)

@main_bp.route('/order/<int:id>')
@login_required
def order_detail(id):
    """Детали заказа"""
    order = Order.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('order.html', order=order)

@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    cart = current_user.cart
    if not cart or not cart.items:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('main.catalog'))

    form = CheckoutForm()
    if form.validate_on_submit():
        try:
            # Создаем заказ из корзины
            order = create_order_from_cart(
                cart=cart,
                shipping_address=form.address.data,
                payment_method=form.payment_method.data,
                shipping_method=form.shipping_method.data
            )
            
            flash('Заказ успешно оформлен!', 'success')
            return redirect(url_for('main.order_detail', id=order.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при оформлении заказа: {str(e)}', 'danger')

    return render_template('checkout.html', form=form, cart=cart)