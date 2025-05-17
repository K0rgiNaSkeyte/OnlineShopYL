import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Получаем DATABASE_URL из переменных окружения
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Создаем соединение с базой данных
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Определяем базовый класс для моделей
Base = declarative_base()


# Определяем модель User
class User(Base):
    __tablename__ = 'users'

    id = Base.metadata.tables['users'].c.id
    email = Base.metadata.tables['users'].c.email
    is_admin = Base.metadata.tables['users'].c.is_admin
    name = Base.metadata.tables['users'].c.name


def make_admin(email):
    # Находим пользователя по email
    user = session.query(User).filter_by(email=email).first()

    if not user:
        print(f'Пользователь с email {email} не найден')
        return

    # Устанавливаем флаг is_admin
    user.is_admin = True
    session.commit()
    print(f'Пользователь {user.email} теперь администратор')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Использование: python make_admin.py <email>')
        sys.exit(1)

    make_admin(sys.argv[1])
