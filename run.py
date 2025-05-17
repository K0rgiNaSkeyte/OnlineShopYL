import os
from app import create_app

# Выбираем конфигурацию на основе переменной окружения
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))