from flask_restful import Resource
from flask_login import login_required
from app.decorators import admin_required
from app.models import Product, Order
from app import db


class AdminProductAPI(Resource):
    @admin_required
    def get(self):
        products = Product.query.all()
        return {'products': [p.to_dict() for p in products]}

    @admin_required
    def post(self):
        pass


class AdminOrderAPI(Resource):
    @admin_required
    def get(self):
        orders = Order.query.all()
        return {'orders': [o.to_dict() for o in orders]}