from flask_restful import Resource, reqparse
from flask_login import login_required, current_user
from app.models import Order, OrderItem
from app.services.order_service import create_order_from_cart
from app import db
from flask import jsonify

class OrderListResource(Resource):
    @login_required
    def get(self):
        """Получение списка заказов пользователя"""
        orders = Order.query.filter_by(user_id=current_user.id).all()
        return {
            'orders': [{
                'id': order.id,
                'date': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'status': order.status,
                'total': float(order.total_amount),
                'items_count': len(order.items)
            } for order in orders]
        }

    @login_required
    def post(self):
        """Создание заказа из корзины"""
        parser = reqparse.RequestParser()
        parser.add_argument('shipping_address', type=str, required=True, help='Не указан адрес доставки')
        parser.add_argument('payment_method', type=str, required=True, help='Не указан способ оплаты')
        parser.add_argument('shipping_method', type=str, required=True, help='Не указан способ доставки')
        args = parser.parse_args()

        cart = current_user.cart
        if not cart or not cart.items:
            return {'success': False, 'error': 'Корзина пуста'}, 400

        try:
            # Создаем заказ из корзины
            order = create_order_from_cart(
                cart=cart,
                shipping_address=args['shipping_address'],
                payment_method=args['payment_method'],
                shipping_method=args['shipping_method']
            )
            
            return {
                'success': True,
                'message': 'Заказ успешно создан',
                'order_id': order.id
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500


class OrderResource(Resource):
    @login_required
    def get(self, order_id):
        """Получение информации о заказе"""
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
        
        items = [{
            'id': item.id,
            'product_id': item.product_id,
            'name': item.product.name if hasattr(item, 'product') and item.product else 'Товар недоступен',
            'price': float(item.price),
            'quantity': item.quantity,
            'total': float(item.price * item.quantity)
        } for item in order.items]
        
        return {
            'id': order.id,
            'date': order.created_at.strftime('%d.%m.%Y %H:%M'),
            'status': order.status,
            'shipping_address': order.shipping_address,
            'payment_method': order.payment_method,
            'shipping_method': order.shipping_method,
            'items': items,
            'subtotal': sum(item['total'] for item in items),
            'shipping_cost': float(order.shipping_cost) if order.shipping_cost else 0,
            'discount': float(order.discount) if order.discount else 0,
            'total': float(order.total_amount)
        }