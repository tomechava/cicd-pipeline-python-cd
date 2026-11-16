"""Aplicación web Flask de la calculadora."""

# app/app.py
import os

from flask import Flask, render_template, request
from .calculadora import sumar, restar, multiplicar, dividir, potencia, modulo

app = Flask(__name__)

# Relaciona cada operación del formulario con su función
OPERACIONES = {
    "sumar": sumar,
    "restar": restar,
    "multiplicar": multiplicar,
    "dividir": dividir,
    "potencia": potencia,
    "modulo": modulo,
}


@app.route("/", methods=["GET", "POST"])
def index():
    """Muestra el formulario y, en POST, calcula el resultado de la operación."""
    resultado = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            funcion = OPERACIONES.get(request.form["operacion"])

            if funcion is None:
                resultado = "Operación no válida"
            else:
                resultado = funcion(num1, num2)
        except ValueError:
            resultado = "Error: Introduce números válidos"
        except ZeroDivisionError:
            resultado = "Error: No se puede dividir por cero"
        except OverflowError:
            resultado = "Error: El resultado es demasiado grande"

    return render_template("index.html", resultado=resultado)


@app.route("/health")
def health():
    """Health check usado por el Load Balancer. Incluye la versión desplegada."""
    return {"status": "ok", "version": os.environ.get("APP_VERSION", "local")}


if __name__ == "__main__":  # pragma: no cover
    # Solo para desarrollo local: sin modo debug y escuchando únicamente en localhost.
    # En el contenedor la sirve Gunicorn, que sí escucha en 0.0.0.0 (ver Dockerfile).
    app.run(port=5000)
