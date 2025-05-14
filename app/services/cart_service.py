from app.models import Cart, CartItem, Product
from app import db
from flask_login import current_user

def get_or_create_cart(user_id):
    """
    Получает существующую корзину пользователя или создает новую
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Cart: Объект корзины
    """
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart

def add_to_cart(user_id, product_id, quantity=1):
    """
    Добавляет товар в корзину пользователя
    
    Args:
        user_id: ID пользователя
        product_id: ID товара
        quantity: Количество товара
        
    Returns:
        CartItem: Добавленный элемент корзины
    """
    # Проверяем существование товара
    product = Product.query.get_or_404(product_id)
    
    # Получаем или создаем корзину
    cart = get_or_create_cart(user_id)
    
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
    return cart_item

def update_cart_item(user_id, item_id, quantity):
    """
    Обновляет количество товара в корзине
    
    Args:
        user_id: ID пользователя
        item_id: ID элемента корзины
        quantity: Новое количество товара
        
    Returns:
        CartItem: Обновленный элемент корзины или None, если элемент был удален
    """
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Проверяем, принадлежит ли товар корзине текущего пользователя
    if cart_item.cart.user_id != user_id:
        raise PermissionError("Доступ запрещен")
    
    if quantity <= 0:
        db.session.delete(cart_item)
        db.session.commit()
        return None
    else:
        cart_item.quantity = quantity
        db.session.commit()
        return cart_item

def remove_from_cart(user_id, item_id):
    """
    Удаляет товар из корзины
    
    Args:
        user_id: ID пользователя
        item_id: ID элемента корзины
        
    Returns:
        bool: True, если удаление прошло успешно
    """
    cart_item = CartItem.query.get_or_404(item_id)
    
    # Проверяем, принадлежит ли товар корзине текущего пользователя
    if cart_item.cart.user_id != user_id:
        raise PermissionError("Доступ запрещен")
    
    db.session.delete(cart_item)
    db.session.commit()
    return True

def clear_cart(user_id):
    """
    Очищает корзину пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        bool: True, если очистка прошла успешно
    """
    cart = Cart.query.filter_by(user_id=user_id).first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    return True

def get_cart_total(cart):
    """
    Рассчитывает общую стоимость корзины
    
    Args:
        cart: Объект корзины
        
    Returns:
        dict: Словарь с информацией о корзине
    """
    if not cart or not cart.items:
        return {
            'items': [],
            'total_items': 0,
            'subtotal': 0,
            'discount': 0,
            'delivery_cost': 0,
            'total': 0
        }
    
    items = [{
        'id': item.id,
        'product_id': item.product_id,
        'name': item.product.name,
        'price': float(item.product.price),
        'quantity': item.quantity,
        'total': float(item.product.price * item.quantity)
    } for item in cart.items]
    
    subtotal = sum(item['total'] for item in items)
    discount = 0  # Здесь можно добавить логику расчета скидки
    delivery_cost = 0  # Здесь можно добавить логику расчета доставки
    
    return {
        'items': items,
        'total_items': sum(item['quantity'] for item in items),
        'subtotal': subtotal,
        'discount': discount,
        'delivery_cost': delivery_cost,
        'total': subtotal - discount + delivery_cost
    }