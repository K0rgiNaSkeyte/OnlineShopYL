import os
from app import create_app
from config import config

# Получаем конфигурацию на основе переменной окружения
env = os.getenv('FLASK_ENV', 'production')
app = create_app(config[env])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))