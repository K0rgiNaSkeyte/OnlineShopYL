from flask_restful import Resource
from app.models import Product
from app import db


class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return {'products': [p.serialize() for p in products]}


class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        return product.serialize()
