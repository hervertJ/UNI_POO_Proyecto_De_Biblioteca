from flask import Flask, render_template, request
from models import Biblioteca, Estudiante, Profesor, Libro, Revista
from datetime import date

app = Flask(__name__)

# Crear la biblioteca y poblarla con algunos datos de ejemplo
biblioteca = Biblioteca()
estudiante = Estudiante(1, "Ana García", "ana@uni.edu", "Ingeniería", 5)
profesor = Profesor(2, "Dr. Pérez", "perez@uni.edu", "Matemáticas", "Tiempo Completo")

libro = Libro(
    101, "Python para Principiantes", "Autor Python", "Editorial Tech", "Programación"
)
revista = Revista(102, "Revista Científica", "Varios Autores", 15, date(2024, 1, 15))

biblioteca.agregar_usuario(estudiante)
biblioteca.agregar_usuario(profesor)
biblioteca.agregar_material(libro)
biblioteca.agregar_material(revista)


@app.route("/")
def home():
    # Mostrar todos los materiales de la biblioteca
    return render_template("index.html", materiales=biblioteca._materiales)


@app.route("/buscar", methods=["POST"])
def buscar():
    palabra = request.form["palabra"]
    resultados = biblioteca._catalogo.buscar_por_palabras_clave(palabra)
    return render_template("index.html", materiales=resultados, palabra=palabra)


if __name__ == "__main__":
    app.run(debug=True)

