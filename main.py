from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/")
def home():
    products = [

    ]
    return render_template("index.html", products=products)


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
