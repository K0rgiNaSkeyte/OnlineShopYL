from flask import Flask, render_template
from pathlib import Path
import os

# Получаем абсолютный путь к папке проекта
BASE_DIR = Path(__file__).parent
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__,
            template_folder=os.path.join(FRONTEND_DIR, 'templates'),
            static_folder=os.path.join(FRONTEND_DIR, 'static'))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print(f"Шаблоны ищутся в: {app.template_folder}")
    print(f"Статика ищется в: {app.static_folder}")
    app.run(debug=True)
