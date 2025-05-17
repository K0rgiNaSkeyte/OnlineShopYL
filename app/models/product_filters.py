from sqlalchemy import or_, and_, func
from app.models import Product, Category

class ProductFilter:
    """Класс для фильтрации товаров"""
    
    def __init__(self, query=None):
        self.query = query if query is not None else Product.query
        
    def filter_by_category(self, category_id):
        """Фильтрация по категории"""
        if category_id:
            # Получаем категорию и все её подкатегории
            category = Category.query.get(category_id)
            if category:
                category_ids = [category.id]
                # Добавляем ID всех дочерних категорий
                for child in category.children:
                    category_ids.append(child.id)
                self.query = self.query.filter(Product.category_id.in_(category_ids))
        return self
        
    def filter_by_price(self, min_price=None, max_price=None):
        """Фильтрация по цене"""
        if min_price is not None:
            self.query = self.query.filter(Product.price >= min_price)
        if max_price is not None:
            self.query = self.query.filter(Product.price <= max_price)
        return self
        
    def filter_by_availability(self, in_stock=None):
        """Фильтрация по наличию"""
        if in_stock is not None:
            self.query = self.query.filter(Product.in_stock == in_stock)
        return self
        
    def search(self, search_term):
        """Поиск по названию и описанию"""
        if search_term:
            search_term = f"%{search_term}%"
            self.query = self.query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        return self
        
    def sort_by(self, sort_option):
        """Сортировка результатов"""
        if sort_option == 'price_asc':
            self.query = self.query.order_by(Product.price.asc())
        elif sort_option == 'price_desc':
            self.query = self.query.order_by(Product.price.desc())
        elif sort_option == 'rating':
            self.query = self.query.order_by(Product.rating.desc())
        elif sort_option == 'newest':
            self.query = self.query.order_by(Product.created_at.desc())
        # По умолчанию сортировка по популярности (можно реализовать через отдельное поле)
        else:
            self.query = self.query.order_by(Product.rating.desc())
        return self
        
    def paginate(self, page=1, per_page=12):
        """Пагинация результатов"""
        return self.query.paginate(page=page, per_page=per_page)
        
    def all(self):
        """Получить все результаты"""
        return self.query.all()