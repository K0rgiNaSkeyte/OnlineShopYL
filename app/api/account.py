from flask_restful import Resource
from flask_login import login_required
from app.models import User, Order
from app import db


class ProfileAPI(Resource):
    @login_required
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return {
            'id': user.id,
            'email': user.email,
            'name': user.name
        }


class OrdersAPI(Resource):
    @login_required
    def get(self, user_id):
        orders = Order.query.filter_by(user_id=user_id).all()
        return {
            'orders': [{
                'id': order.id,
                'total': order.total_amount,
                'date': order.created_at.isoformat()
            } for order in orders]
        }


def register_account_resources(api):
    api.add_resource(ProfileAPI, '/profile/<int:user_id>')
    api.add_resource(OrdersAPI, '/orders/<int:user_id>')
