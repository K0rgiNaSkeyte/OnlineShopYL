from flask_restful import Api
from app.api import api_bp
from .resources.products import ProductResource, ProductListResource
from .resources.cart import CartResource, CartItemResource
from .resources.orders import OrderResource, OrderListResource
from .resources.users import UserResource
from .account import ProfileAPI, OrdersAPI
from .admin.resources import AdminProductAPI, AdminOrderAPI

# Создаем API
api = Api(api_bp)

def register_api_resources():
    # Ресурсы для товаров
    api.add_resource(ProductListResource, '/products')
    api.add_resource(ProductResource, '/products/<int:product_id>')
    
    # Ресурсы для корзины
    api.add_resource(CartResource, '/cart')
    api.add_resource(CartItemResource, '/cart/items/<int:item_id>')
    
    # Ресурсы для заказов
    api.add_resource(OrderListResource, '/orders')
    api.add_resource(OrderResource, '/orders/<int:order_id>')
    
    # Ресурсы для пользователей
    api.add_resource(UserResource, '/users/<int:user_id>')
    
    # Ресурсы для аккаунта
    api.add_resource(ProfileAPI, '/profile/<int:user_id>')
    api.add_resource(OrdersAPI, '/user/orders/<int:user_id>')
    
    # Ресурсы для админа
    api.add_resource(AdminProductAPI, '/admin/products')
    api.add_resource(AdminOrderAPI, '/admin/orders')