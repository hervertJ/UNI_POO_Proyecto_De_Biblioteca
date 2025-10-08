from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    # return "12345"
    data = {"titulo": "Index", "bienvenida": "Saludsos"}
    return render_template("index.html", data=data)


@app.route("/contacto/<nombre>")
def contacto(nombre):
    data = {"titulo": "contacto", "nombre": nombre}
    return render_template("contanto.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
