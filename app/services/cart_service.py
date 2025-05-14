from app.models import Cart, CartItem, Product
from app import db

def get_or_create_cart(user_id):
    """
    Получение или создание корзины для пользователя
    """
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart

def add_to_cart(user_id, product_id, quantity=1):
    """
    Добавление товара в корзину
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

def get_cart_total(cart):
    """
    Расчет итогов корзины
    """
    if not cart or not cart.items:
        return {
            'items': [],
            'total': 0,
            'total_items': 0,
            'subtotal': 0,
            'discount': 0,
            'delivery_cost': 0
        }
    
    items = []
    subtotal = 0
    total_items = 0
    
    for item in cart.items:
        product = item.product
        if product:
            item_total = product.price * item.quantity
            subtotal += item_total
            total_items += item.quantity
            
            items.append({
                'id': item.id,
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': item.quantity,
                'total': item_total,
                'image': product.image_url,
                'category': product.category.name if product.category else 'Без категории'
            })
    
    # Расчет скидки (пример: 5% от суммы заказа)
    discount = round(subtotal * 0.05, 2) if subtotal > 0 else 0
    
    # Расчет стоимости доставки (пример: бесплатно от 5000 руб.)
    delivery_cost = 0 if subtotal >= 5000 else 300
    
    # Итоговая сумма
    total = subtotal - discount + delivery_cost
    
    return {
        'items': items,
        'total': total,
        'total_items': total_items,
        'subtotal': subtotal,
        'discount': discount,
        'delivery_cost': delivery_cost
    }

def remove_from_cart(user_id, item_id):
    """
    Удаление товара из корзины
    """
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return False
    
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not cart_item:
        return False
    
    db.session.delete(cart_item)
    db.session.commit()
    return True

def clear_cart(user_id):
    """
    Очистка корзины
    """
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return False
    
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()
    return True