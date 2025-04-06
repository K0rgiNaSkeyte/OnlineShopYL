import sqlalchemy
from data.db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = "categories"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    slug = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
