from waitress import serve
from app import create_app

app = create_app()

if __name__ == '__main__':
    print('Запуск сервера на http://localhost:8080')
    serve(app, host='0.0 0.0', port=8080)