import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase


class Cart(SqlAlchemyBase):
    __tablename__ = "carts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("users.id"), nullable=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="carts")
    items = relationship("CartItem", backref="cart")


class CartItem(SqlAlchemyBase):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    cart_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("carts.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("products.id"))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=1)

    product = relationship("Product")
