from flask_login import current_user


def cart_processor():
    """
    Контекстный процессор для подсчета товаров в корзине
    """
    cart_count = 0
    if current_user.is_authenticated:
        cart = current_user.cart
        if cart and cart.items:
            cart_count = sum(item.quantity for item in cart.items)

    return {'cart_count': cart_count}
