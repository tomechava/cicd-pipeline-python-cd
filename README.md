# entregable-2-cicd

Pipeline de Integración Continua para una calculadora web en Flask, con GitHub Actions, Docker, SonarCloud y publicación en Docker Hub.

## Integrantes

`AUTOR`: Santiago Alvarez | Emmanuel Correa | Tomás Echavarria | José David Toro

| Nombre completo | Usuario de GitHub | Rol |
|---|---|---|
| Santiago Alvarez | SantiagoAlvP | Colaborador |
| Emmanuel Correa | imKorr | Colaborador |
| Tomás Echavarria | tomechava | **Propietario del repositorio** |
| José David Toro | josedtf | Colaborador |

## Evidencias

- Pull Request de la sección 9: https://github.com/tomechava/entregable-2-cicd/pull/1
- Ejecución fallida por el error intencional: https://github.com/tomechava/entregable-2-cicd/actions/runs/43543289549

## Respuestas

### 1. Ventajas de un pipeline de CI

- **Detección temprana de errores.** Cada push y cada Pull Request ejecutan pruebas y análisis automáticamente, así que un fallo se encuentra minutos después de introducirlo y no semanas después. Corregirlo es más barato porque el cambio aún está fresco.
- **Calidad consistente y verificable.** Black, Pylint, Flake8, la cobertura mínima del 80% y el Quality Gate de SonarCloud se aplican siempre y a todos, sin depender de que alguien se acuerde de correrlos. El estándar de calidad deja de depender de la disciplina individual.
- **Integración segura en equipo.** Con la rama `main` protegida, ningún cambio entra sin que el pipeline esté en verde y otro integrante lo apruebe. Esto evita que el trabajo de una persona rompa el de las demás.
- **Entrega reproducible y automática.** La imagen Docker se construye y se publica siempre con el mismo procedimiento, sin pasos manuales propensos a error, y queda trazada al commit exacto (etiqueta SHA).

### 2. Pruebas unitarias, de componente y de aceptación

La aplicación es una **calculadora web en Flask**: un formulario con dos números y una operación (sumar, restar, multiplicar, dividir) que muestra el resultado.

- **Unitaria:** prueba una función aislada, sin servidor ni navegador. Ejemplo: `dividir(1, 0)` debe lanzar `ZeroDivisionError`.
- **De componente:** prueba la aplicación Flask (ruta, lógica y plantilla HTML juntas) con el cliente de pruebas de Flask, sin levantar un servidor real ni un navegador. Ejemplo: un POST con `num1='6'`, `num2='0'` y `operacion='dividir'` debe devolver la página con "Error: No se puede dividir por cero".
- **De aceptación:** prueba la aplicación como lo haría un usuario, con un navegador real (Selenium) sobre la app corriendo en su contenedor Docker. Ejemplo: abrir la página, escribir 2 y 3, elegir "Sumar", pulsar "Calcular" y verificar que se vea "Resultado: 5.0".

### 3. Steps del workflow

1. **Checkout** (`actions/checkout`): descarga el código del repositorio en el runner, con historial completo (`fetch-depth: 0`) para que SonarCloud identifique el código nuevo.
2. **Set up Python** (`actions/setup-python`): instala Python 3.13, la misma versión del Dockerfile y de desarrollo, para que el entorno sea consistente.
3. **Install dependencies:** instala `requirements-dev.txt` (linters, pytest, Selenium, etc.) con versiones fijas para que el pipeline sea reproducible.
4. **Run Black** (`--check`): verifica que el código esté formateado. Si no lo está, detiene el pipeline, para mantener un estilo uniforme.
5. **Run Pylint** y **Run Flake8** (`--exit-zero`): generan los reportes `pylint-report.txt` y `flake8-report.txt`. Los hallazgos no detienen el pipeline porque SonarCloud los consolida y decide con el Quality Gate.
6. **Run Unit and Component Tests:** ejecuta las pruebas unitarias y de componente y exige cobertura total de al menos 80%. Genera `coverage.xml` para SonarCloud.
7. **Build Docker image:** construye la imagen una sola vez y la etiqueta con el SHA del commit, para que cada versión sea identificable y no ambigua.
8. **Start container:** ejecuta la imagen en segundo plano (puerto 8000) y espera a que la app responda, para poder probarla como se ejecutaría realmente.
9. **Run Acceptance Tests:** ejecuta las pruebas de Selenium contra el contenedor (`APP_BASE_URL=http://localhost:8000`), validando la imagen real y no solo el código.
10. **Show container logs on failure** (`if: failure()`): muestra los logs del contenedor si algo falló, para facilitar el diagnóstico.
11. **Upload Test Reports Artifacts** (`actions/upload-artifact`, `if: always()`): sube los reportes aunque el pipeline falle, para poder revisarlos.
12. **SonarCloud Scan:** envía el código y los reportes a SonarCloud y falla si el Quality Gate no es `Passed`, para impedir que código sin calidad suficiente avance.
13. **Login to Docker Hub** (`docker/login-action`): autentica con la variable `DOCKERHUB_USERNAME` y el secreto `DOCKERHUB_TOKEN`. Solo en push a `main`.
14. **Push Docker image:** agrega la etiqueta `latest` a la imagen ya probada y publica `latest` y SHA en Docker Hub. Solo en push a `main`, y sin reconstruir la imagen.

### 4. Problemas y aprendizajes

**Santiago Alvarez:** Tuve un problema con los tokens y las credenciales. El paso `Login to Docker Hub` o `SonarCloud Scan` fallaba por autenticación, y la causa era que había guardado el valor con un nombre distinto o en el lugar equivocado. Aprendí que `SONAR_TOKEN` y `DOCKERHUB_TOKEN` van como **secretos** (cifrados), mientras que `DOCKERHUB_USERNAME` y `SONAR_HOST_URL` van como **variables** (configuración no sensible), y que los nombres deben coincidir exactamente con los del workflow. También aprendí que el token de Docker Hub se muestra una sola vez al generarlo, por lo que hay que copiarlo de inmediato, y que nunca se deben escribir tokens en el código, el README ni los logs.

**Emmanuel Correa:** Mi aprendizaje fue sobre Black. Mi primer push falló en el paso `Run Black` porque no había formateado el código antes del commit. Entendí que en el pipeline Black corre con `--check`, que solo verifica y no modifica, así que cualquier archivo sin formatear detiene todo. La solución fue ejecutar `black app` localmente, volver a hacer commit y push. Desde entonces lo ejecuto antes de cada commit, y vi que también reduce hallazgos de estilo en Pylint y Flake8. Además aprendí que el archivo `.flake8` con `max-line-length = 88` hace que Flake8 y Black sean compatibles.

**Tomás Echavarria:** Aprendí a usar SonarCloud y a interpretar su Quality Gate. En la primera ejecución el paso `SonarCloud Scan` falló y al principio no entendía por qué si las pruebas habían pasado. Al abrir el enlace del log vi que el Quality Gate evaluaba el código nuevo y que el código inicial tenía issues de Security, Reliability y Maintainability. Aprendí a leer las pestañas "Why is this an issue?" y "How can I fix it?" de cada hallazgo, a corregir los que aplicaban y a aceptar con un comentario de justificación los que no (por ejemplo, la protección CSRF en una app sin sesiones). También aprendí que hay que desactivar el Automatic Analysis, configurar New Code en 30 días y hacer público el proyecto para que el análisis del pipeline funcione y se pueda calificar.

**José David Toro:** Tuve un problema con Docker, porque el contenedor no respondía en el pipeline. Al probar localmente, la aplicación no abría en el puerto esperado. Entendí que Gunicorn escucha en el puerto 8000 dentro del contenedor, por eso el mapeo era `-p 8080:8000` en local y `-p 8000:8000` en el pipeline, y que `app.run(host='0.0.0.0')` es necesario para que la app sea accesible fuera del contenedor. También aprendí que la imagen solo debe contener lo necesario para ejecutarse (por eso hay `requirements.txt` separado de `requirements-dev.txt`) y que `.dockerignore` evita copiar archivos locales. Por último, el nombre del repositorio debía estar en minúsculas, porque Docker no acepta mayúsculas en el nombre de la imagen.

### 5. Ventajas de construir, probar y publicar la misma imagen

- **Se prueba lo que realmente se entrega.** Validar solo el código no garantiza que la imagen funcione: el Dockerfile podría omitir una dependencia o copiar mal los archivos. Las pruebas de aceptación sobre el contenedor detectan esos fallos.
- **Sin diferencias entre "lo probado" y "lo publicado".** Como se construye una sola vez y se publica esa misma imagen (con etiqueta SHA), no hay una segunda construcción que pueda comportarse distinto.
- **Reproducibilidad y trazabilidad.** La imagen empaqueta la aplicación con sus dependencias, y la etiqueta SHA la vincula con el commit exacto que pasó todas las validaciones. Esto facilita volver a una versión anterior y prepara el despliegue del Taller 3.
- **Ahorro de tiempo y consistencia entre entornos.** El mismo artefacto se ejecuta igual en el pipeline, en un computador local o en un servidor.

### 6. Pull Request de la sección 9

**Pruebas agregadas y qué detectan:**

| Prueba | Qué error detectaría |
|---|---|
| `test_operaciones_con_decimales` | Errores con decimales en cualquiera de las 4 operaciones, como redondeos o conversiones a entero. También detecta el error intencional, porque `restar(0.3, 0.1)` daría 0.4 en vez de 0.2. |
| `test_operaciones_con_dos_negativos` | Errores de signo, como multiplicar dos negativos y obtener negativo. También detecta el error intencional, porque `restar(-5, -3)` daría -8 en vez de -2. |
| `test_index_post_restar_negativos` | Errores en la ruta web al restar negativos. También detecta el error intencional, porque la página mostraría "Resultado: -8.0" en vez de "-2.0". |
| `test_index_post_un_numero_invalido` | Que la app deje de validar cuando solo uno de los dos campos es inválido, o que falle con un error 500 en vez de mostrar el mensaje de error. |

**Error intencional (`restar` devolvía `a + b`):**

- **Paso donde falló:** `Run Unit and Component Tests`. Las pruebas de resta fallaron, tanto las originales como las nuevas, y los pasos anteriores (Black, Pylint y Flake8) habían pasado.
- **Pasos que no se ejecutaron:** `Build Docker image`, `Start container`, `Run Acceptance Tests`, `SonarCloud Scan`, `Login to Docker Hub` y `Push Docker image`. Se ejecutaron solo los pasos de diagnóstico y de subida de reportes (`failure()` y `always()`).
- **Cómo se impidió que llegara a `main` y a Docker Hub:**
  - La regla `proteger-main` exige que el check `build-and-test` esté en verde y que haya una aprobación, así que GitHub bloqueó el merge mientras el check estaba en rojo.
  - Aun sin esa regla, la publicación solo ocurre en un push a `main` y solo si todos los pasos anteriores fueron exitosos. Como el pipeline se detuvo en las pruebas, ni se construyó la imagen ni se publicó.
  - Al corregir `restar` el pipeline volvió a verde, se aprobó el PR y solo entonces se integró y se publicó la imagen.