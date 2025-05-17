from app.api import api
from app.api.resources.products import ProductListResource, ProductResource, SearchResource

# Регистрация ресурсов API
api.add_resource(ProductListResource, '/products')
api.add_resource(ProductResource, '/products/<int:product_id>')
api.add_resource(SearchResource, '/search')

def register_api_resources():
    """Функция для регистрации API ресурсов"""
    # Ресурсы уже зарегистрированы выше
    pass