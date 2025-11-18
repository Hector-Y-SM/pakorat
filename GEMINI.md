# GEMINI.md (Español)

## Resumen del Proyecto

Este proyecto, "Pakkorat Uno", es una implementación digital del juego de cartas Baccarat que utiliza un método de entrada novedoso: un feed de video en vivo que detecta cartas físicas. Las cartas son las de un juego UNO estándar (valores del 0 al 9 en cuatro colores) que han sido aumentadas con códigos QR.

La aplicación está construida en Python y utiliza OpenCV para la interfaz de usuario y la visión por computadora, `pyzbar` para la decodificación de códigos QR y `reportlab` para generar las hojas de QR imprimibles.

La arquitectura es modular:
- **`main.py`**: El punto de entrada principal que maneja la configuración inicial del usuario (elección de cámara, tamaño de pantalla) y lanza el juego.
- **`interfaz.py`**: Gestiona la interfaz gráfica del juego usando OpenCV. Renderiza el estado del juego, el feed de la cámara y captura la entrada del teclado del usuario.
- **`juego_baccarat.py`**: Un módulo de lógica pura que contiene la máquina de estados y las reglas del juego de Baccarat. Está completamente desacoplado de la interfaz de usuario.
- **`detector_cartas.py`**: Se encarga de todas las tareas de visión por computadora. Se conecta a una cámara web local o IP, detecta objetos con forma de carta y decodifica los códigos QR en ellos para identificar el valor y el color de la carta.
- **`generar_qr.py`**: Un script de utilidad para generar un PDF imprimible (`etiquetas_uno_qr.pdf`) que contiene todos los códigos QR que deben ser pegados en las cartas físicas de UNO.
- **`requirements.txt`**: Lista todas las dependencias de Python necesarias.

## Funcionamiento Detallado de la Detección de Cartas

El componente de visión por computadora en `detector_cartas.py` es crucial para el funcionamiento del juego. A continuación, se explica su mecanismo en mayor profundidad.

#### ¿Qué es un `frame`?

Un video, en esencia, no es más que una sucesión de imágenes fijas mostradas a gran velocidad. Cada una de estas imágenes se conoce como un **`frame`**. La cámara (ya sea local o IP) captura estas imágenes continuamente. El programa procesa cada `frame` de forma individual para analizar la escena, detectar cartas y actualizar la interfaz. El `frame` es, por tanto, la materia prima sobre la que opera toda la lógica de visión.

#### Proceso de Detección en Dos Etapas

Para que la detección sea eficiente y precisa, no se busca un código QR en toda la imagen del `frame` de manera indiscriminada. En su lugar, se sigue un proceso de dos etapas:

1.  **Etapa 1: Encontrar la Carta (Rectángulo Blanco)**
    *   El primer paso es localizar objetos que parezcan una carta de UNO. Dado que estas cartas tienen un borde blanco distintivo, el programa realiza una serie de operaciones con OpenCV para encontrarlas:
    *   Convierte el `frame` a escala de grises.
    *   Aplica un umbral (`thresholding`) para resaltar únicamente las áreas muy brillantes (blancas) de la imagen.
    *   Busca los contornos o formas (`contours`) en la imagen umbralizada.
    *   Filtra estos contornos para quedarse solo con aquellos que son grandes y tienen una forma aproximadamente rectangular.
    *   Este proceso aísla las "regiones de interés" (ROI), es decir, las áreas del `frame` donde es muy probable que haya una carta.

2.  **Etapa 2: Buscar el Código QR dentro de la Carta**
    *   Una vez que se ha identificado la ubicación de una posible carta (un rectángulo blanco), el programa recorta esa pequeña porción del `frame`.
    *   **Solo sobre esta pequeña región recortada** se ejecuta el decodificador de códigos QR (`pyzbar`).
    *   Este enfoque es mucho más rápido y robusto que intentar encontrar un QR en la totalidad del `frame`, ya que reduce el área de búsqueda y minimiza las posibilidades de falsos positivos.

#### Anotación del Frame y Visualización

El `frame` que el usuario ve en la ventana del juego no es la imagen cruda de la cámara. Es un **`frame` anotado**. Después de que la lógica de detección y del juego se ejecuta, el programa "dibuja" información visual sobre el `frame` antes de mostrarlo. Esto incluye:
*   Rectángulos de colores alrededor de las cartas detectadas (azul para una carta potencial, verde para una confirmada con QR).
*   El texto con la información de la carta (ej. "Rojo 7").
*   El panel lateral con los puntos, el estado del juego y los controles.

De este modo, el `frame` se convierte en el lienzo sobre el que se construye toda la interfaz gráfica del juego.

## Instalación y Ejecución

Para ejecutar este proyecto, primero necesitas configurar un entorno virtual de Python e instalar las dependencias requeridas. También necesitarás una cámara web (ya sea integrada o una aplicación de cámara IP en un smartphone) y un juego de cartas UNO con los códigos QR generados adjuntos.

### 1. Configurar el Entorno Virtual

Es muy recomendable utilizar un entorno virtual para evitar conflictos con otros proyectos de Python.

```bash
# Crear un entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

### 2. Instalar Dependencias

Instala todos los paquetes necesarios usando pip y el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 3. Generar y Preparar las Cartas (Configuración única)

Si aún no lo has hecho, ejecuta el script `generar_qr.py` para crear el archivo `etiquetas_uno_qr.pdf`.

```bash
python generar_qr.py
```

Imprime este PDF, recorta los códigos QR y pégalos en las cartas físicas de UNO correspondientes (0-9 para cada uno de los cuatro colores).

### 4. Ejecutar el Juego

Lanza la aplicación ejecutando el script `main.py`.

```bash
python main.py
```

La aplicación te pedirá que:
1.  Selecciones el tamaño de la ventana.
2.  Elijas tu tipo de cámara (webcam local o IP webcam).

Sigue las instrucciones en pantalla para jugar.

## Convenciones de Desarrollo

- **Modularidad**: El proyecto se divide en módulos distintos con responsabilidades claras (UI, lógica del juego, detección de cartas).
- **Gestión de Estado**: La lógica central del juego en `juego_baccarat.py` se implementa como una máquina de estados, lo que hace que el flujo del juego sea predecible y más fácil de gestionar.
- **Configuración**: Los ajustes específicos del usuario, como la elección de la cámara y el tamaño de la ventana, se configuran en tiempo de ejecución a través de una interfaz de línea de comandos en `main.py`.
- **Controles**: El juego se controla mediante atajos de teclado, que se muestran en la interfaz de usuario.
  - `ESPACIO`: Iniciar una nueva ronda.
  - `R`: Reiniciar el juego después de que termine una ronda.
  - `D`: Activar/desactivar la vista de depuración para la detección de cartas.
  - `Q`: Salir de la aplicación.