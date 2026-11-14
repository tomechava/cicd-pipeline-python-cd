# tests/test_acceptance_app.py
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")


# Configuración del driver (elige uno: Chrome o Firefox)
@pytest.fixture
def browser():
    # Opción 1: Chrome (headless - sin interfaz gráfica)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecuta sin interfaz gráfica
    options.add_argument("--no-sandbox")  # Necesario para algunos entornos
    options.add_argument("--disable-dev-shm-usage")  # Necesario para algunos entornos
    # Chrome reciente usa "HTTPS por defecto": ante un sitio público en http:// intenta
    # https:// y, como el ALB solo escucha en el puerto 80, muestra una página de aviso
    # en lugar de la calculadora. Se desactiva para poder probar Staging por HTTP.
    options.add_argument(
        "--disable-features=HttpsUpgrades,HttpsFirstModeV2,"
        "HttpsFirstBalancedModeAutoEnable,HttpsFirstModeV2ForTypicallySecureUsers"
    )
    options.add_experimental_option("prefs", {"https_only_mode_enabled": False})
    driver = webdriver.Chrome(options=options)

    yield driver
    driver.quit()


# Función de ayuda: espera hasta 10 segundos a que el <h2> sea visible y devuelve su texto.
# Si no aparece, Selenium lanza TimeoutException y la prueba falla mostrando la causa.
def get_resultado(browser):
    resultado = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h2"))
    )
    return resultado.text


# Función de ayuda para encontrar los elementos del formulario
def find_elements(browser):
    num1_input = browser.find_element(By.NAME, "num1")
    num2_input = browser.find_element(By.NAME, "num2")
    operacion_select = Select(browser.find_element(By.NAME, "operacion"))
    calcular_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    return num1_input, num2_input, operacion_select, calcular_button


@pytest.mark.parametrize(
    "num1, num2, operacion, resultado_esperado",
    [
        ("2", "3", "sumar", "Resultado: 5.0"),
        ("5", "2", "restar", "Resultado: 3.0"),
        ("4", "6", "multiplicar", "Resultado: 24.0"),
        ("10", "2", "dividir", "Resultado: 5.0"),
        ("5", "0", "dividir", "Resultado: Error: No se puede dividir por cero"),
        ("abc", "def", "sumar", "Resultado: Error: Introduce números válidos"),
    ],
)
def test_calculadora(browser, num1, num2, operacion, resultado_esperado):
    browser.get(BASE_URL)

    num1_input, num2_input, operacion_select, calcular_button = find_elements(browser)

    num1_input.send_keys(num1)
    num2_input.send_keys(num2)
    operacion_select.select_by_value(operacion)
    calcular_button.click()

    # Compara el texto completo: "Resultado: 5.0" no debe aceptar "Resultado: 50.0"
    assert get_resultado(browser) == resultado_esperado