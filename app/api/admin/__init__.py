from flask_restful import Api
from .resources import AdminProductAPI, AdminOrderAPI


def register_admin_resources(api):
    api.add_resource(AdminProductAPI, '/admin/products')
    api.add_resource(AdminOrderAPI, '/admin/orders')
