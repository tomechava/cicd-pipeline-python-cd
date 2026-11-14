"""Aplicación web Flask de la calculadora."""

# app/app.py
import os

from flask import Flask, render_template, request
from .calculadora import sumar, restar, multiplicar, dividir

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Muestra el formulario y, en POST, calcula el resultado de la operación."""
    resultado = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operacion = request.form["operacion"]

            if operacion == "sumar":
                resultado = sumar(num1, num2)
            elif operacion == "restar":
                resultado = restar(num1, num2)
            elif operacion == "multiplicar":
                resultado = multiplicar(num1, num2)
            elif operacion == "dividir":
                resultado = dividir(num1, num2)
            else:
                resultado = "Operación no válida"
        except ValueError:
            resultado = "Error: Introduce números válidos"
        except ZeroDivisionError:
            resultado = "Error: No se puede dividir por cero"

    return render_template("index.html", resultado=resultado)


@app.route("/health")
def health():
    """Health check usado por el Load Balancer. Incluye la versión desplegada."""
    return {"status": "ok", "version": os.environ.get("APP_VERSION", "local")}


if __name__ == "__main__":  # pragma: no cover
    # Solo para desarrollo local: sin modo debug y escuchando únicamente en localhost.
    # En el contenedor la sirve Gunicorn, que sí escucha en 0.0.0.0 (ver Dockerfile).
    app.run(port=5000)
