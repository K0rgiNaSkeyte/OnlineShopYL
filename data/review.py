import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase


class Review(SqlAlchemyBase):
    __tablename__ = "reviews"

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("users.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("goods.id"))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="reviews")
    product_id = relationship("Product", backref="reviews")
