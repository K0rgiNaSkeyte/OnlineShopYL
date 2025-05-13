from .resources.products import ProductResource, ProductListResource
from .resources.users import UserResource

def register_api_resources(api):
    api.add_resource(ProductListResource, '/products')
    api.add_resource(ProductResource, '/products/<int:product_id>')
    api.add_resource(UserResource, '/users/<int:user_id>')