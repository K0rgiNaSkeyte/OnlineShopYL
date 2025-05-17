from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Order, OrderItem, Product
from app.forms import CheckoutForm
from app.services.cart_service import get_cart_total, clear_cart
from app import db
from datetime import datetime
from . import main_bp

@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Страница оформления заказа"""
    # Проверяем, есть ли товары в корзине
    cart = current_user.cart
    if not cart or not cart.items:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('main.cart'))
    
    # Получаем данные корзины
    cart_data = get_cart_total(cart)
    
    # Создаем форму оформления заказа
    form = CheckoutForm()
    
    # Предзаполняем адрес из профиля пользователя, если он есть
    if request.method == 'GET' and current_user.profile and current_user.profile.address:
        form.shipping_address.data = current_user.profile.address
    
    return render_template('checkout.html',
                          form=form,
                          cart_items=cart_data['items'],
                          total=cart_data['total'],
                          total_items=cart_data['total_items'],
                          subtotal=cart_data['subtotal'],
                          discount=cart_data['discount'],
                          delivery_cost=cart_data['delivery_cost'])

@main_bp.route('/checkout/process', methods=['POST'])
@login_required
def process_checkout():
    """Обработка оформления заказа"""
    # Проверяем, есть ли товары в корзине
    cart = current_user.cart
    if not cart or not cart.items:
        flash('Ваша корзина пуста', 'warning')
        return redirect(url_for('main.cart'))
    
    # Получаем данные корзины
    cart_data = get_cart_total(cart)
    
    # Валидируем форму
    form = CheckoutForm()
    if not form.validate_on_submit():
        return render_template('checkout.html',
                              form=form,
                              cart_items=cart_data['items'],
                              total=cart_data['total'],
                              total_items=cart_data['total_items'],
                              subtotal=cart_data['subtotal'],
                              discount=cart_data['discount'],
                              delivery_cost=cart_data['delivery_cost'])
    
    try:
        # Создаем новый заказ с учетом существующей структуры БД
        order = Order(
            user_id=current_user.id,
            shipping_address=form.shipping_address.data,
            payment_method=form.payment_method.data,
            status='created',
            total_price=cart_data['total']
        )
        
        # Сохраняем информацию о способе доставки и примечаниях в адресе
        shipping_info = f"Способ доставки: {form.shipping_method.data}"
        if form.notes.data:
            shipping_info += f"\nПримечания: {form.notes.data}"
        
        # Добавляем эту информацию к адресу доставки
        order.shipping_address = f"{order.shipping_address}\n\n{shipping_info}"
        
        db.session.add(order)
        db.session.flush()  # Получаем ID заказа
        
        # Добавляем товары из корзины в заказ
        for item in cart.items:
            product = Product.query.get(item.product_id)
            if product:
                # Проверяем наличие товара на складе
                if product.stock < item.quantity:
                    flash(f'Товар "{product.name}" доступен только в количестве {product.stock} шт.', 'danger')
                    return redirect(url_for('main.cart'))
                
                # Уменьшаем количество товара на с��ладе
                product.stock -= item.quantity
                if product.stock <= 0:
                    product.in_stock = False
                
                # Добавляем товар в заказ
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    price=product.price
                )
                db.session.add(order_item)
        
        # Очищаем корзину
        clear_cart(current_user.id)
        
        # Сохраняем изменения в БД
        db.session.commit()
        
        flash('Заказ успешно оформлен! Корзина очищена.', 'success')
        return redirect(url_for('main.order_success', order_id=order.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при оформлении заказа: {str(e)}', 'danger')
        return redirect(url_for('main.checkout'))

@main_bp.route('/orders')
@login_required
def orders():
    """Страница заказов пользователя"""
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@main_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """Страница деталей заказа"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Извлекаем информацию о способе доставки из адреса
    shipping_method = "Стандартная доставка"
    notes = ""
    
    if order.shipping_address and "Способ доставки:" in order.shipping_address:
        address_parts = order.shipping_address.split("\n\n")
        if len(address_parts) > 1:
            shipping_info = address_parts[1].split("\n")
            for info in shipping_info:
                if info.startswith("Способ доставки:"):
                    shipping_method = info.replace("Способ доставки:", "").strip()
                elif info.startswith("Примечания:"):
                    notes = info.replace("Примечания:", "").strip()
            
            # Очищаем адрес от дополнительной информации
            order.clean_address = address_parts[0]
        else:
            order.clean_address = order.shipping_address
    else:
        order.clean_address = order.shipping_address
    
    # Добавляем информацию к объекту заказа
    order.shipping_method = shipping_method
    order.notes = notes
    
    return render_template('order_detail.html', order=order)

@main_bp.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    """Страница успешного оформления заказа"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    # Извлекаем информацию о способе доставки из адреса
    shipping_method = "Стандартная доставка"
    notes = ""
    
    if order.shipping_address and "Способ доставки:" in order.shipping_address:
        address_parts = order.shipping_address.split("\n\n")
        if len(address_parts) > 1:
            shipping_info = address_parts[1].split("\n")
            for info in shipping_info:
                if info.startswith("Способ доставки:"):
                    shipping_method = info.replace("Способ доставки:", "").strip()
                elif info.startswith("Примечания:"):
                    notes = info.replace("Примечания:", "").strip()
            
            # Очищаем адрес от дополнительной информации
            order.clean_address = address_parts[0]
        else:
            order.clean_address = order.shipping_address
    else:
        order.clean_address = order.shipping_address
    
    # Добавляем информацию к объекту заказа
    order.shipping_method = shipping_method
    order.notes = notes
    
    return render_template('order_success.html', order=order)