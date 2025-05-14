from app.models import Order, OrderItem, Cart
from app import db
from datetime import datetime

def create_order_from_cart(cart, shipping_address, payment_method, shipping_method):
    """
    Создает заказ на основе корзины пользователя
    
    Args:
        cart: Объект корзины пользователя
        shipping_address: Адрес доставки
        payment_method: Способ оплаты
        shipping_method: Способ доставки
        
    Returns:
        Order: Созданный заказ
    """
    if not cart or not cart.items:
        raise ValueError("Корзина пуста")
    
    # Рассчитываем стоимость доставки (можно добавить более сложную логику)
    shipping_cost = 0
    if shipping_method == 'express':
        shipping_cost = 500
    elif shipping_method == 'standard':
        shipping_cost = 300
    
    # Рассчитываем скидку (можно добавить более сложную логику)
    discount = 0
    
    # Рассчитываем общую сумму заказа
    subtotal = sum(item.product.price * item.quantity for item in cart.items)
    total_amount = subtotal + shipping_cost - discount
    
    # Создаем заказ
    order = Order(
        user_id=cart.user_id,
        status='new',
        shipping_address=shipping_address,
        payment_method=payment_method,
        shipping_method=shipping_method,
        shipping_cost=shipping_cost,
        discount=discount,
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )
    
    db.session.add(order)
    db.session.flush()  # Получаем ID заказа
    
    # Создаем элементы заказа на основе элементов корзины
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            price=cart_item.product.price,
            quantity=cart_item.quantity
        )
        db.session.add(order_item)
    
    # Очищаем корзину
    for item in cart.items:
        db.session.delete(item)
    
    db.session.commit()
    return order