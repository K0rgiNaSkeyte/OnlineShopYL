from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Главная страница"


@app.route("/about")
def about():
    return "О магазине"


if __name__ == '__main__':
    app.run()
