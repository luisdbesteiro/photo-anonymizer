# Anonimizador de caras y matriculas

Herramienta local para detectar caras y posibles matriculas en fotografias, anonimizarlas y guardar copias procesadas sin modificar los originales.

## Instalacion en Windows

1. Instala Python 3 desde <https://www.python.org/downloads/>.
2. Durante la instalacion de Python, marca la opcion **Add python.exe to PATH**.
3. Haz doble clic en `install_windows.bat`.
4. Haz doble clic en `models\download_models_windows.bat` si necesitas descargar de nuevo los modelos.
5. Espera a que aparezca el mensaje de modelos listos.

## Ejecutar la aplicacion

Haz doble clic en `run_app.bat`.

Se abrira una ventana donde puedes:

- Seleccionar imagenes sueltas.
- Seleccionar una carpeta completa.
- Elegir la carpeta de salida.
- Elegir desenfoque, pixelado o recuadro negro.
- Activar o desactivar deteccion de caras y matriculas.
- Activar `Guardar anotadas (debug)` para guardar copias con caras, matriculas y vehiculos detectados dibujados.
- Abrir `Confianzas avanzadas` para ajustar los umbrales con sliders si necesitas afinar la deteccion.

Al seleccionar una carpeta, la salida se propone automaticamente en una carpeta nueva junto a la original, con el sufijo `_anonimizadas`. Por ejemplo, si eliges `C:\Fotos\Coches`, la salida sera `C:\Fotos\Coches_anonimizadas`.

Las confianzas avanzadas mantienen por defecto los valores recomendados de la aplicacion. Bajarlas puede detectar mas zonas, pero tambien puede generar mas falsos positivos.

Si activas el modo debug, se crea otra carpeta junto a la original con el sufijo `_anotadas`. Por ejemplo, `C:\Fotos\Coches` guardara esas copias en `C:\Fotos\Coches_anotadas`.
Las imagenes anotadas muestran las detecciones de caras, matriculas y vehiculos que superan las confianzas actuales, con su etiqueta y puntuacion. Sirven para diagnosticar los modelos; no son necesariamente solo las zonas finalmente anonimizadas.

Las imagenes procesadas se guardan como copias con nombres como:

```text
foto_001_anonimizada.jpg
```

La herramienta intenta conservar en las copias anonimizadas los metadatos de la fotografia original, como EXIF, perfil de color, DPI y textos de PNG cuando el formato lo permite. Ten en cuenta que esos metadatos pueden incluir informacion sensible, por ejemplo ubicacion GPS si la camara o el movil la guardo.

## Desinstalar en Windows

Haz doble clic en `uninstall_windows.bat`.

El script elimina el entorno virtual `.venv`, que es donde se instalan las dependencias de Python de esta herramienta. Tambien puede borrar, si lo confirmas, los modelos descargados, los logs y las carpetas de salida locales.

No desinstala Python del ordenador y no borra automaticamente tus fotos originales ni carpetas de salida creadas junto a tus fotos.

## Carpetas

- `fotos/`: fotos originales o de prueba.
- `output/`: salida de reserva si no se ha seleccionado ninguna carpeta de entrada.
- `logs/`: registro de errores y procesamientos.
- `src/`: codigo de la aplicacion.
- `models/`: modelos YOLO preentrenados.

## Modelos YOLO

La deteccion usa modelos YOLO preentrenados colocados en:

```text
models/yolo_faces.pt
models/yolo_plates.pt
models/yolov8n.pt
```

Necesitas tres modelos:

- Uno entrenado para detectar caras.
- Otro entrenado para detectar matriculas.
- Un modelo COCO general para detectar vehiculos y filtrar falsos positivos de matriculas.

No uses un modelo YOLO general de COCO como unica solucion, porque normalmente no detecta matriculas ni caras como clases especificas. Si los modelos faltan, la aplicacion mostrara un aviso antes de procesar.

Para uso interno, puedes descargar los modelos recomendados con:

```bash
python models/download_models.py
```

En Windows, despues de instalar dependencias, puedes hacer doble clic en:

```text
models\download_models_windows.bat
```

El script crea `models/MODELS_DOWNLOADED.md` con origen, licencia declarada y fecha de descarga.

Esta herramienta esta planteada para uso interno. No redistribuirla fuera de la organizacion sin revisar de nuevo las licencias de `ultralytics`, de los modelos y de sus datasets.

## Importante

La deteccion automatica puede fallar, especialmente con matriculas lejanas, inclinadas, borrosas o parcialmente tapadas. Revisa siempre las imagenes procesadas antes de compartirlas.

El procesamiento se hace localmente en el ordenador. La herramienta no sube fotos a internet ni intenta identificar personas.

## Ejecutar en Ubuntu

Si quieres abrir la interfaz grafica en Linux, instala primero Tkinter si tu distribucion no lo trae:

```bash
sudo apt install python3-tk
```

Despues puedes lanzarla desde la raiz del proyecto con:

```bash
./run_app_linux.sh
```

Tambien puedes ejecutarla directamente con:

```bash
source .venv/bin/activate
python3 -m src.main
```

No uses `python3 src/main.py`, porque la aplicacion esta organizada como paquete Python y necesita arrancar como modulo.

Si necesitas descargar de nuevo los modelos desde Ubuntu:

```bash
python3 -m pip install -r requirements.txt
python3 models/download_models.py
```

## Si algo falla

- Ejecuta de nuevo `install_windows.bat`.
- Comprueba que Python esta instalado y agregado al PATH.
- Revisa si se creo un archivo en `logs/anonimizador.log`.
- Si una imagen concreta da error, prueba con otra imagen `.jpg`, `.jpeg` o `.png`.
