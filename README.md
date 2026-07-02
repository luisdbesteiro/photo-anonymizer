# Anonimizador de caras y matriculas

Herramienta local para detectar caras y posibles matriculas en fotografias, anonimizarlas y guardar copias procesadas sin modificar los originales.

## Instalacion en Windows

1. Instala Python 3 desde <https://www.python.org/downloads/>.
2. Durante la instalacion de Python, marca la opcion **Add python.exe to PATH**.
3. Haz doble clic en `run_app.bat`.
4. Espera a que se instalen las dependencias y se descarguen los modelos.
5. Si la descarga de modelos falla, revisa la conexion a internet y ejecuta `installer_scripts\download_models_windows.bat` mas tarde.

Tambien puedes hacer doble clic en `installer_scripts\install_windows.bat` si prefieres instalar todo antes de abrir la aplicacion.

## Ejecutar la aplicacion

Haz doble clic en `run_app.bat`. Si no hay instalacion previa, el script la prepara automaticamente y despues abre la aplicacion.

Se abrira una ventana donde puedes:

- Seleccionar imagenes sueltas.
- Seleccionar una carpeta completa.
- Elegir la carpeta de salida.
- Elegir desenfoque, pixelado o recuadro negro.
- Activar o desactivar deteccion de caras y matriculas.
- Activar `Guardar anotadas (debug)` para guardar copias con caras, matriculas y vehiculos detectados dibujados.
- Abrir `Confianzas avanzadas` para ajustar los umbrales con sliders si necesitas afinar la deteccion.

Al seleccionar una carpeta, la salida se propone automaticamente en una carpeta nueva junto a la original, con el sufijo `_pixeladas`. Por ejemplo, si eliges `C:\Fotos\Coches`, la salida sera `C:\Fotos\Coches_pixeladas`.

Las confianzas avanzadas mantienen por defecto los valores recomendados de la aplicacion. Bajarlas puede detectar mas zonas, pero tambien puede generar mas falsos positivos.

Si activas el modo debug, se crea otra carpeta junto a la original con el sufijo `_anotadas`. Por ejemplo, `C:\Fotos\Coches` guardara esas copias en `C:\Fotos\Coches_anotadas`.
Las imagenes anotadas muestran las detecciones de caras, matriculas y vehiculos que superan las confianzas actuales, con su etiqueta y puntuacion. Sirven para diagnosticar los modelos; no son necesariamente solo las zonas finalmente anonimizadas.

Las imagenes procesadas se guardan como copias con nombres como:

```text
foto_001.jpg
```

La herramienta intenta conservar en las copias anonimizadas los metadatos de la fotografia original, como EXIF, perfil de color, DPI y textos de PNG cuando el formato lo permite. Ten en cuenta que esos metadatos pueden incluir informacion sensible, por ejemplo ubicacion GPS si la camara o el movil la guardo.

## Desinstalar en Windows

Haz doble clic en `installer_scripts\uninstall_windows.bat`.

El script elimina el entorno virtual `.venv`, que es donde se instalan las dependencias de Python de esta herramienta. Tambien puede borrar, si lo confirmas, los modelos descargados, los logs y las carpetas de salida locales.

No desinstala Python del ordenador y no borra automaticamente tus fotos originales ni carpetas de salida creadas junto a tus fotos.

## Carpetas

- `logs/`: registro de errores y procesamientos.
- `src/`: codigo de la aplicacion.
- `models/`: modelos YOLO preentrenados.
- `installer_scripts/`: instalacion, desinstalacion, dependencias y utilidades auxiliares.
- `input/`: carpeta opcional para dejar imagenes de entrada.
- `output/`: carpeta opcional para resultados locales.

La raiz del proyecto queda reservada para lo esencial:

- `run_app.bat`: archivo principal para abrir la herramienta en Windows.
- `README.md`: instrucciones de uso.
- `AGENTS.md`: notas internas para desarrollo.

## Modelos YOLO

La deteccion usa modelos YOLO preentrenados colocados en:

```text
models/yolo_faces.pt
models/yolo_plates.pt
models/yolov8n.pt
```

Necesitas tres modelos:

- Uno entrenado para detectar caras. El modelo recomendado para la prueba tambien detecta personas, pero la aplicacion filtra solo la clase `face`.
- Otro entrenado para detectar matriculas.
- Un modelo COCO general para detectar vehiculos y filtrar falsos positivos de matriculas.

No uses un modelo YOLO general de COCO como unica solucion, porque normalmente no detecta matriculas ni caras como clases especificas. Si los modelos faltan, la aplicacion mostrara un aviso antes de procesar.

Para uso interno, puedes descargar los modelos recomendados con:

```bash
python src/download_models.py
```

Para sustituir solo el modelo de caras por el recomendado actualmente:

```bash
python src/download_models.py --only caras --force
```

En Windows, despues de instalar dependencias, puedes hacer doble clic en:

```text
installer_scripts\download_models_windows.bat
```

Normalmente no hace falta ejecutar ese archivo durante la primera instalacion, porque `installer_scripts\install_windows.bat` ya descarga los modelos. Usalo si necesitas reintentar la descarga.

El script crea `models/MODELS_DOWNLOADED.md` con origen, licencia declarada y fecha de descarga.

Esta herramienta esta planteada para uso interno. No redistribuirla fuera de la organizacion sin revisar de nuevo las licencias de `ultralytics`, de los modelos y de sus datasets.

## Importante

La deteccion automatica puede fallar, especialmente con matriculas lejanas, inclinadas, borrosas o parcialmente tapadas. Revisa siempre las imagenes procesadas antes de compartirlas.

El procesamiento se hace localmente en el ordenador. La herramienta no sube fotos a internet ni intenta identificar personas.

## Si algo falla

- Ejecuta de nuevo `run_app.bat` o `installer_scripts\install_windows.bat`.
- Comprueba que Python esta instalado y agregado al PATH.
- Revisa si se creo un archivo en `logs/anonimizador.log`.
- Si una imagen concreta da error, prueba con otra imagen `.jpg`, `.jpeg` o `.png`.
