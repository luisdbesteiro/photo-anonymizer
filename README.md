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

Al seleccionar una carpeta, la salida se propone automaticamente en una carpeta nueva junto a la original, con el sufijo `_anonimizadas`. Por ejemplo, si eliges `C:\Fotos\Coches`, la salida sera `C:\Fotos\Coches_anonimizadas`.

Las imagenes procesadas se guardan como copias con nombres como:

```text
foto_001_anonimizada.jpg
```

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

## Prueba en Ubuntu

Para probar la deteccion y anonimizacion sin abrir la interfaz grafica:

```bash
python3 -m pip install -r requirements.txt
python3 models/download_models.py
python3 run_ubuntu_test.py --input fotos --output output_ubuntu_test --limit 10
```

Opciones utiles:

```bash
python3 run_ubuntu_test.py --input una_foto.jpg --method pixelado
python3 run_ubuntu_test.py --input fotos --no-faces
python3 run_ubuntu_test.py --input fotos --no-plates
python3 run_ubuntu_test.py --input fotos --face-model models/yolo_faces.pt --plate-model models/yolo_plates.pt
```

Las imagenes originales no se modifican.

### Diagnostico de detecciones

Para ver todas las clases detectadas por los modelos, sin anonimizar:

```bash
python3 run_ubuntu_test.py --diagnostic --input fotos --output output/diagnostico
```

Para revisar candidatos de baja confianza:

```bash
python3 run_ubuntu_test.py --diagnostic --input fotos --output output/diagnostico_baja_confianza --diagnostic-plate-confidence 0.01
```

El modo diagnostico guarda imagenes con cajas y etiquetas como `coco:car 0.91` o `matriculas:vehicle 0.49`.
Por defecto usa estos umbrales: caras `>0.6`, matriculas `>0.4`, vehiculos `>0.2`.
Cuando usas `--diagnostic-models vehicles`, solo se muestran clases COCO de vehiculos: `bicycle`, `car`, `motorcycle`, `bus` y `truck`.

## Si algo falla

- Ejecuta de nuevo `install_windows.bat`.
- Comprueba que Python esta instalado y agregado al PATH.
- Revisa si se creo un archivo en `logs/anonimizador.log`.
- Si una imagen concreta da error, prueba con otra imagen `.jpg`, `.jpeg` o `.png`.
