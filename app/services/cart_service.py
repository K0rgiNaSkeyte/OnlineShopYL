from app.models import Cart, CartItem, Product
from app import db

def get_or_create_cart(user_id):
    """Получение или создание корзины для пользователя"""
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart

def add_to_cart(user_id, product_id, quantity=1):
    """Добавление товара в корзину"""
    # Проверяем существование товара
    product = Product.query.get(product_id)
    if not product:
        raise ValueError("Товар не найден")
    
    # Проверяем наличие товара на складе
    if quantity > product.stock:
        raise ValueError(f"Доступно только {product.stock} шт.")
    
    # Получаем или создаем корзину
    cart = get_or_create_cart(user_id)
    
    # Проверяем, есть ли уже такой товар в корзине
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if cart_item:
        # Если товар уже есть, увеличиваем количество
        cart_item.quantity += quantity
    else:
        # Если товара нет, создаем новую запись
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    return cart_item

def update_cart_item(item_id, quantity):
    """Обновление количества товара в корзине"""
    cart_item = CartItem.query.get(item_id)
    if not cart_item:
        raise ValueError("Товар в корзине не найден")
    
    # Проверяем наличие товара на складе
    product = Product.query.get(cart_item.product_id)
    if quantity > product.stock:
        raise ValueError(f"Доступно только {product.stock} шт.")
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    return cart_item

def remove_from_cart(item_id):
    """Удаление товара из корзины"""
    cart_item = CartItem.query.get(item_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
    return True

def clear_cart(user_id):
    """Очистка корзины пользователя"""
    cart = Cart.query.filter_by(user_id=user_id).first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    return True

def get_cart_total(cart):
    """Расчет итоговой суммы корзины"""
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
        product = Product.query.get(item.product_id)
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
                'image': product.image_url or '/static/img/no-image.png',
                'category': product.category.name if product.category else 'Без категории'
            })
    
    # Расчет скидки (пример: 5% от суммы заказа)
    discount = round(subtotal * 0.05, 2) if subtotal > 0 else 0
    
    # Стоимость доставки (пример: бесплатно от 3000 руб.)
    delivery_cost = 0 if subtotal >= 3000 else 300
    
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