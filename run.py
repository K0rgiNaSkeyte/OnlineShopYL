import os
from app import create_app
from config import ProductionConfig, DevelopmentConfig

# Выбираем конфигурацию на основе переменной окружения
if os.getenv('FLASK_ENV') == 'development':
    app = create_app(DevelopmentConfig)
else:
    app = create_app(ProductionConfig)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))