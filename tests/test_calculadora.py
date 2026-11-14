# tests/test_calculadora.py
import pytest
from app.calculadora import sumar, restar, multiplicar, dividir

def test_sumar():
    assert sumar(2, 3) == 5
    assert sumar(-1, 1) == 0
    assert sumar(0, 0) == 0

def test_restar():
    assert restar(5, 2) == 3
    assert restar(1, -1) == 2
    assert restar(0, 0) == 0

def test_multiplicar():
    assert multiplicar(2, 3) == 6
    assert multiplicar(-1, 5) == -5
    assert multiplicar(0, 10) == 0

def test_dividir():
    assert dividir(10, 2) == 5.0
    assert dividir(5, -1) == -5.0
    with pytest.raises(ZeroDivisionError):
        dividir(1, 0)

def test_operaciones_con_decimales():
    # 0.1 + 0.2 no es exactamente 0.3 en punto flotante: se compara con approx
    assert sumar(0.1, 0.2) == pytest.approx(0.3)
    assert restar(0.3, 0.1) == pytest.approx(0.2)
    assert multiplicar(1.5, 2.5) == pytest.approx(3.75)
    assert dividir(1, 3) == pytest.approx(0.3333333)


def test_operaciones_con_dos_negativos():
    assert sumar(-2, -3) == -5
    assert restar(-5, -3) == -2
    assert multiplicar(-4, -2) == 8
    assert dividir(-9, -3) == 3.0
