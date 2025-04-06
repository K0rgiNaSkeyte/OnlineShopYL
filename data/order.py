import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = "orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("users.id"))
    total_price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String, default="created")
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    address = sqlalchemy.Column(sqlalchemy.String)
    phone = sqlalchemy.Column(sqlalchemy.String)

    user = relationship("User", backref="orders")
    items = relationship("OrderItems", backref="order")


class OrderItem(SqlAlchemyBase):
    __tablename__ = "order_items"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, ForeingKey("orders.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("products.id"))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    product = relationship("Product")
