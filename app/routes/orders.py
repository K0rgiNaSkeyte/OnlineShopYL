from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Order, Cart
from app.forms import CheckoutForm
from . import main_bp


@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    cart = current_user.cart
    if not cart or not cart.items:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('main.product_list'))

    form = CheckoutForm()
    if form.validate_on_submit():
        # Создание заказа
        return redirect(url_for('orders.thank_you'))

    return render_template('orders/checkout.html', form=form, cart=cart)


@main_bp.route('/orders/<int:id>')
@login_required
def order_details(id):
    """Детали заказа"""
    order = Order.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('orders/detail.html', order=order)
