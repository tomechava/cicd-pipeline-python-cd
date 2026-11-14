# tests/test_smoke_app.py
"""Pruebas de humo: verifican rápidamente que la aplicación desplegada responde."""
import json
import os
from urllib.request import urlopen

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")
EXPECTED_VERSION = os.environ.get("EXPECTED_VERSION")


def test_pagina_principal_carga():
    """La página principal responde 200 y muestra la calculadora."""
    with urlopen(BASE_URL + "/", timeout=10) as response:
        assert response.status == 200
        html = response.read().decode("utf-8")
    assert "Calculadora" in html


def test_health_y_version():
    """El health check responde 'ok' y, si se indica, la versión esperada."""
    with urlopen(BASE_URL + "/health", timeout=10) as response:
        assert response.status == 200
        datos = json.load(response)
    assert datos["status"] == "ok"
    if EXPECTED_VERSION:
        assert datos["version"] == EXPECTED_VERSION