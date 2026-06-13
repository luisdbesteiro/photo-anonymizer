# AGENTS.md

## Objetivo del proyecto

Ayudar a desarrollar una herramienta para **detectar y anonimizar matrículas y caras en fotografías**.

La herramienta debe estar pensada para ser usada en **varios equipos Windows** por personas que **no están acostumbradas a programar ni usar terminales**. Por tanto, el resultado final debe ser lo más sencillo posible de instalar y ejecutar.

El objetivo principal no es hacer una demo técnica, sino crear una utilidad práctica, clara y mantenible.

---

## Funcionalidad principal

El proyecto debe permitir:

1. Seleccionar una o varias fotografías.
2. Detectar automáticamente:

   * Caras.
   * Matrículas de vehículos.
3. Aplicar anonimización sobre esas zonas:

   * Preferiblemente desenfoque fuerte.
   * Opcionalmente pixelado o recuadro negro si se implementa como opción.
4. Guardar las imágenes procesadas en una carpeta de salida.
5. Mantener las imágenes originales sin modificar.
6. Generar nombres de salida claros, por ejemplo:

   * `foto_001_anonimizada.jpg`
   * `foto_001_blurred.jpg`

---

## Prioridades de diseño

La prioridad es la **facilidad de uso en Windows**.

La solución debe evitar que el usuario final tenga que escribir comandos manualmente.

Siempre que sea posible, el proyecto debe incluir:

* Un script de instalación de dependencias.
* Un script para ejecutar la aplicación.
* Una interfaz gráfica sencilla.
* Mensajes claros de error y éxito.
* Una estructura de carpetas comprensible.
* Instrucciones breves en un `README.md`.

---

## Público objetivo

El usuario final puede no saber:

* Qué es Python.
* Qué es pip.
* Qué es un entorno virtual.
* Cómo abrir una terminal.
* Cómo instalar dependencias manualmente.

Por tanto, cualquier solución debe intentar ocultar o automatizar estos pasos.

---

## Plataforma objetivo

El proyecto debe estar pensado principalmente para:

* Windows 10.
* Windows 11.

No es necesario priorizar Linux o macOS salvo que se indique expresamente.

---

## Requisitos técnicos recomendados

Usar Python como lenguaje principal.

Priorizar dependencias fáciles de instalar en Windows.

Dependencias recomendadas inicialmente:

* `opencv-python`
* `pillow`
* `numpy`
* `tkinter` si se usa interfaz gráfica nativa, teniendo en cuenta que suele venir con Python.
* Opcionalmente `ultralytics` si se decide usar YOLO para detección de matrículas o caras, pero solo si compensa la complejidad.

Evitar dependencias difíciles de instalar en Windows salvo que sean claramente necesarias.

---

## Estructura recomendada del proyecto

La estructura inicial recomendada es:

```text
proyecto_anonimizador/
├── AGENTS.md
├── README.md
├── requirements.txt
├── install_windows.bat
├── run_app.bat
├── src/
│   ├── main.py
│   ├── gui.py
│   ├── detector_faces.py
│   ├── detector_plates.py
│   ├── anonymizer.py
│   └── utils.py
├── input/
├── output/
├── models/
└── logs/
```

Explicación:

* `src/main.py`: punto de entrada principal.
* `src/gui.py`: interfaz gráfica para usuarios no técnicos.
* `src/detector_faces.py`: lógica de detección de caras.
* `src/detector_plates.py`: lógica de detección de matrículas.
* `src/anonymizer.py`: desenfoque, pixelado o tapado de zonas detectadas.
* `src/utils.py`: funciones auxiliares.
* `input/`: carpeta opcional para imágenes de entrada.
* `output/`: carpeta donde guardar imágenes anonimizadas.
* `models/`: modelos externos si se usan.
* `logs/`: logs de ejecución.

---

## Instalación en Windows

El proyecto debe incluir un archivo:

```text
install_windows.bat
```

Este archivo debe:

1. Comprobar si Python está disponible.
2. Crear un entorno virtual local, por ejemplo `.venv`.
3. Activar el entorno virtual.
4. Instalar las dependencias desde `requirements.txt`.
5. Mostrar mensajes claros al usuario.
6. Pausar al final para que el usuario pueda leer si hubo errores.

Ejemplo de comportamiento esperado:

```text
Instalando herramienta de anonimización...
Comprobando Python...
Creando entorno virtual...
Instalando dependencias...
Instalación completada.
Puedes ejecutar la aplicación usando run_app.bat
```

No asumir que el usuario sabe interpretar errores largos de pip. Si algo falla, mostrar un mensaje simple indicando que debe revisar si Python está instalado y añadido al PATH.

---

## Ejecución en Windows

El proyecto debe incluir un archivo:

```text
run_app.bat
```

Este archivo debe:

1. Activar el entorno virtual.
2. Ejecutar la aplicación principal.
3. Mostrar un mensaje claro si falta la instalación previa.
4. Pausar en caso de error.

El usuario final debería poder ejecutar la aplicación haciendo doble clic en `run_app.bat`.

---

## Interfaz gráfica

Priorizar una interfaz gráfica sencilla antes que una herramienta solo por terminal.

La interfaz debería permitir:

* Seleccionar imágenes individuales.
* Seleccionar una carpeta completa de imágenes.
* Elegir carpeta de salida.
* Elegir tipo de anonimización:

  * Desenfoque.
  * Pixelado.
  * Recuadro negro.
* Activar o desactivar:

  * Detectar caras.
  * Detectar matrículas.
* Lanzar el procesamiento con un botón.
* Mostrar progreso básico.
* Mostrar resumen final:

  * Número de imágenes procesadas.
  * Número de errores.
  * Carpeta de salida.

No sobrecargar la interfaz. Debe ser clara y simple.

---

## Detección de caras

Para una primera versión funcional, se puede usar OpenCV.

Opciones posibles:

1. Haar Cascade de OpenCV:

   * Fácil de usar.
   * Sin modelos pesados.
   * Menor precisión.

2. DNN face detector de OpenCV:

   * Mejor precisión.
   * Puede requerir archivos de modelo adicionales.

3. YOLO u otro modelo:

   * Mejor para detección avanzada.
   * Más dependencias.
   * Más complejidad para instalación en Windows.

Priorizar una solución robusta y fácil de instalar.

Si se usa un modelo externo, debe documentarse:

* Dónde se guarda.
* Cómo se descarga.
* Si se incluye en el repositorio o no.
* Qué hacer si falta el archivo.

---

## Detección de matrículas

La detección de matrículas puede ser más compleja que la de caras.

Opciones aceptables:

1. Primera versión con heurísticas OpenCV:

   * Búsqueda de rectángulos.
   * Detección de bordes.
   * Filtrado por proporciones típicas de matrículas.
   * Puede fallar más.

2. Modelo entrenado o preentrenado:

   * Más fiable.
   * Más complejo.
   * Puede requerir archivos en `models/`.

3. Sistema híbrido:

   * Primero detección automática.
   * Luego posibilidad de revisar o añadir zonas manualmente.

Para este proyecto, valorar mucho la posibilidad de añadir una función de **revisión manual**, porque la detección automática de matrículas puede fallar.

---

## Anonimización

La anonimización debe aplicarse únicamente sobre las zonas detectadas.

Crear funciones separadas para:

* Desenfoque fuerte.
* Pixelado.
* Relleno negro.

La anonimización debe ser irreversible de forma práctica. No usar desenfoques demasiado suaves.

Ejemplo de parámetros recomendados:

* Gaussian blur fuerte con kernel grande.
* Pixelado reduciendo mucho la resolución de la región y reescalando.
* Rectángulo negro sólido.

---

## Seguridad y privacidad

Este proyecto se usa para proteger privacidad.

No implementar funciones de identificación de personas.

No implementar reconocimiento facial.

No implementar lectura OCR de matrículas salvo que sea estrictamente necesario para mejorar la detección, y en ese caso no guardar ni mostrar el texto detectado.

No subir imágenes a servicios externos.

Todo el procesamiento debe hacerse localmente en el ordenador del usuario.

Las imágenes originales no deben modificarse nunca.

---

## Gestión de errores

El programa debe manejar errores de forma clara.

Casos a contemplar:

* Imagen corrupta.
* Formato no soportado.
* Carpeta de salida inexistente.
* Permisos insuficientes.
* Falta de dependencias.
* Falta de modelos.
* Imagen demasiado grande.
* No se detectan caras ni matrículas.

Los errores deben mostrarse de forma comprensible para usuarios no técnicos.

También se recomienda guardar un log en `logs/`.

---

## Formatos de imagen

Soportar como mínimo:

* `.jpg`
* `.jpeg`
* `.png`

Opcionalmente:

* `.bmp`
* `.tiff`
* `.webp`

Conservar el formato original cuando sea razonable.

---

## README.md esperado

El proyecto debe incluir un `README.md` sencillo, orientado a usuarios de Windows.

Debe explicar:

1. Qué hace la herramienta.
2. Cómo instalarla.
3. Cómo ejecutarla.
4. Cómo seleccionar imágenes.
5. Dónde se guardan los resultados.
6. Qué hacer si algo falla.
7. Advertencia de que la detección automática puede no ser perfecta.
8. Recomendación de revisar las imágenes antes de compartirlas.

No escribir un README excesivamente técnico.

---

## Estilo de código

Mantener el código:

* Claro.
* Modular.
* Comentado donde aporte valor.
* Fácil de modificar.
* Sin abstracciones innecesarias.

Evitar crear una arquitectura demasiado compleja.

Priorizar funciones pequeñas y nombres descriptivos.

---

## Criterios de calidad

Antes de considerar una versión como válida, comprobar que:

* La instalación funciona desde cero en Windows.
* La aplicación se puede abrir con doble clic.
* Se pueden procesar varias imágenes.
* Las imágenes originales no se modifican.
* Las imágenes procesadas aparecen en `output/` o en la carpeta elegida.
* Las caras detectadas quedan correctamente anonimizadas.
* Las matrículas detectadas quedan correctamente anonimizadas.
* Si no se detecta nada, el programa no falla.
* Los errores se muestran de forma clara.

---

## Posibles fases de desarrollo

### Fase 1: prototipo funcional

* Script básico en Python.
* Selección de carpeta de entrada y salida.
* Detección de caras.
* Anonimización por desenfoque.
* Guardado en carpeta de salida.

### Fase 2: matrículas

* Añadir detección de matrículas.
* Probar con varias fotos reales.
* Ajustar falsos positivos y falsos negativos.

### Fase 3: interfaz gráfica

* Crear GUI simple.
* Añadir botones y opciones básicas.
* Ocultar complejidad al usuario.

### Fase 4: instalación sencilla

* Crear `requirements.txt`.
* Crear `install_windows.bat`.
* Crear `run_app.bat`.
* Redactar `README.md`.

### Fase 5: revisión y mejora

* Añadir logs.
* Añadir revisión manual de zonas.
* Mejorar precisión.
* Preparar una versión portable si es viable.

---

## Reglas para Codex

Cuando trabajes en este proyecto:

1. No asumas que el usuario final sabe usar terminal.
2. No propongas soluciones que dependan de subir imágenes a internet.
3. No modifiques imágenes originales.
4. No implementes reconocimiento facial ni identificación de personas.
5. Prioriza Windows.
6. Prioriza instalación sencilla.
7. Antes de añadir una dependencia pesada, justifica por qué es necesaria.
8. Mantén la estructura de archivos ordenada.
9. Cuando generes código, incluye instrucciones claras de uso.
10. Si hay varias alternativas, prioriza la más robusta y fácil de mantener.
11. Si una detección automática puede fallar, indícalo y propone revisión manual.
12. Evita soluciones excesivamente complejas para una primera versión.
13. El resultado debe poder ser utilizado por personas no técnicas.
14. Incluye siempre scripts auxiliares cuando ahorren trabajo al usuario final.
15. Documenta claramente cualquier modelo externo necesario.

---

## Resultado final deseado

El resultado ideal del proyecto será una carpeta que se pueda copiar a varios equipos Windows y que permita:

1. Ejecutar `install_windows.bat` una vez.
2. Ejecutar `run_app.bat` cuando se quiera usar la herramienta.
3. Abrir una interfaz gráfica sencilla.
4. Seleccionar fotos o carpetas.
5. Anonimizar caras y matrículas.
6. Guardar copias procesadas.
7. Revisar los resultados antes de compartir las imágenes.

El proyecto debe priorizar utilidad real, privacidad y facilidad de uso.

