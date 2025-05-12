from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def about():
    return render_template("index_auth.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/catalog")
def catalog():
    return render_template("catalog.html")


if __name__ == '__main__':
    app.run()
