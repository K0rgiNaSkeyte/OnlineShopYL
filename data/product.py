import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = "products"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("categories.id"))
    stock = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    modified_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    image_url = sqlalchemy.Column(sqlalchemy.String)

    category = sqlalchemy.relationship("Category", backref="products")
