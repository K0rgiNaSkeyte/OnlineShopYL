import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Получаем DATABASE_URL из переменных окружения или используем локальную SQLite базу
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/shop.db')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Подключение к базе данных: {DATABASE_URL}")

# Создаем соединение с базой данных
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Определяем модель User
class User(object):
    __tablename__ = 'users'
    
    def __init__(self, id=None, email=None, is_admin=None, name=None):
        self.id = id
        self.email = email
        self.is_admin = is_admin
        self.name = name

def make_admin(email):
    # Выполняем прямой SQL-запрос для обновления
    try:
        result = session.execute(f"UPDATE users SET is_admin = TRUE WHERE email = '{email}'")
        session.commit()
        
        if result.rowcount > 0:
            print(f'Пользователь с email {email} теперь администратор')
        else:
            print(f'Пользователь с email {email} не найден')
    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        session.rollback()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Использование: python make_admin.py <email>')
        sys.exit(1)
    
    make_admin(sys.argv[1])