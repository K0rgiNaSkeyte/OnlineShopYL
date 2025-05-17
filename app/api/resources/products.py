from flask_restful import Resource, reqparse
from app.models import Product, Category
from app import db
from sqlalchemy import or_, and_, func


class ProductListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('category_id', type=int, location='args')
        self.parser.add_argument('min_price', type=float, location='args')
        self.parser.add_argument('max_price', type=float, location='args')
        self.parser.add_argument('in_stock', type=bool, location='args')
        self.parser.add_argument('q', type=str, location='args')
        self.parser.add_argument('sort', type=str, choices=['price_asc', 'price_desc', 'rating', 'newest', 'popular'], 
                                location='args', default='popular')
        self.parser.add_argument('page', type=int, location='args', default=1)
        self.parser.add_argument('per_page', type=int, location='args', default=12)
        super(ProductListResource, self).__init__()

    def get(self):
        args = self.parser.parse_args()
        
        # Базовый запрос
        query = Product.query
        
        # Фильтр по категории
        if args['category_id']:
            category = Category.query.get(args['category_id'])
            if category:
                # Получаем ID всех подкатегорий
                category_ids = [category.id]
                for child in Category.query.filter_by(parent_id=category.id).all():
                    category_ids.append(child.id)
                query = query.filter(Product.category_id.in_(category_ids))
        
        # Фильтр по цене
        if args['min_price'] is not None:
            query = query.filter(Product.price >= args['min_price'])
        if args['max_price'] is not None:
            query = query.filter(Product.price <= args['max_price'])
        
        # Фильтр по наличию
        if args['in_stock'] is not None:
            query = query.filter(Product.in_stock == args['in_stock'])
        
        # Поиск по названию и описанию
        if args['q']:
            search_term = f"%{args['q']}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Сортировка
        if args['sort'] == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif args['sort'] == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif args['sort'] == 'rating':
            query = query.order_by(Product.rating.desc())
        elif args['sort'] == 'newest':
            query = query.order_by(Product.created_at.desc())
        else:  # По умолчанию по популярности (рейтингу)
            query = query.order_by(Product.rating.desc())
        
        # Пагинация
        page = args['page']
        per_page = args['per_page']
        
        paginated_products = query.paginate(page=page, per_page=per_page)
        
        return {
            'products': [p.serialize() for p in paginated_products.items],
            'total': paginated_products.total,
            'pages': paginated_products.pages,
            'page': page,
            'per_page': per_page,
            'has_next': paginated_products.has_next,
            'has_prev': paginated_products.has_prev,
            'next_page': paginated_products.next_num if paginated_products.has_next else None,
            'prev_page': paginated_products.prev_num if paginated_products.has_prev else None
        }


class ProductResource(Resource):
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        
        # Получаем похожие товары из той же категории
        similar_products = []
        if product.category_id:
            similar_products = Product.query.filter(
                Product.category_id == product.category_id,
                Product.id != product.id
            ).order_by(Product.rating.desc()).limit(4).all()
        
        result = product.serialize()
        result['similar_products'] = [p.serialize() for p in similar_products]
        
        return result


class SearchResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('q', type=str, required=True, location='args')
        super(SearchResource, self).__init__()
    
    def get(self):
        args = self.parser.parse_args()
        search_term = f"%{args['q']}%"
        
        products = Product.query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        ).order_by(Product.rating.desc()).limit(10).all()
        
        return {'results': [p.serialize() for p in products]}