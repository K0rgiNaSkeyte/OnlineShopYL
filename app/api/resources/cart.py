from flask_restful import Resource, reqparse
from flask_login import login_required, current_user
from app.models import Cart, CartItem, Product
from app import db
from flask import jsonify

class CartResource(Resource):
    @login_required
    def get(self):
        """Получение содержимого корзины"""
        cart = current_user.cart
        if not cart:
            return {'items': [], 'total': 0}

        items = [{
            'id': item.id,
            'product_id': item.product_id,
            'name': item.product.name,
            'price': float(item.product.price),
            'quantity': item.quantity,
            'image': item.product.image if hasattr(item.product, 'image') else None,
            'total': float(item.product.price * item.quantity)
        } for item in cart.items]

        return {
            'items': items,
            'total_items': sum(item['quantity'] for item in items),
            'subtotal': sum(item['total'] for item in items),
            'discount': 0,  # Здесь можно добавить логику расчета скидки
            'delivery_cost': 0,  # Здесь можно добавить логику расчета доставки
            'total': sum(item['total'] for item in items)
        }

    @login_required
    def post(self):
        """Добавление товара в корзину"""
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', type=int, required=True, help='Не указан ID товара')
        parser.add_argument('quantity', type=int, default=1)
        args = parser.parse_args()

        product = Product.query.get_or_404(args['product_id'])
        
        # Получаем или создаем корзину для пользователя
        cart = current_user.cart
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        
        # Проверяем, есть ли уже такой товар в корзине
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=args['product_id']).first()
        
        if cart_item:
            # Если товар уже в корзине, увеличиваем количество
            cart_item.quantity += args['quantity']
        else:
            # Иначе добавляем новый товар
            cart_item = CartItem(cart_id=cart.id, product_id=args['product_id'], quantity=args['quantity'])
            db.session.add(cart_item)
        
        db.session.commit()
        
        return {'success': True, 'message': 'Товар добавлен в корзину'}

    @login_required
    def delete(self):
        """Очистка корзины"""
        cart = current_user.cart
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
        
        return {'success': True, 'message': 'Корзина очищена'}


class CartItemResource(Resource):
    @login_required
    def put(self, item_id):
        """Обновление количества товара в корзине"""
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', type=int, required=True, help='Не указано количество')
        args = parser.parse_args()
        
        cart_item = CartItem.query.get_or_404(item_id)
        
        # Проверяем, принадлежит ли товар корзине текущего пользователя
        if cart_item.cart.user_id != current_user.id:
            return {'success': False, 'error': 'Доступ запрещен'}, 403
        
        if args['quantity'] <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = args['quantity']
        
        db.session.commit()
        
        return {'success': True, 'message': 'Количество товара обновлено'}

    @login_required
    def delete(self, item_id):
        """Удаление товара из корзины"""
        cart_item = CartItem.query.get_or_404(item_id)
        
        # Проверяем, принадлежит ли товар корзине текущего пользователя
        if cart_item.cart.user_id != current_user.id:
            return {'success': False, 'error': 'Доступ запрещен'}, 403
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return {'success': True, 'message': 'Товар удален из корзины'}