# Modelos YOLO

Coloca aqui los modelos YOLO preentrenados:

```text
models/yolo_faces.pt
models/yolo_plates.pt
models/yolov8n.pt
```

Importante:

- `yolo_faces.pt` debe estar entrenado para detectar caras.
- `yolo_plates.pt` debe estar entrenado para detectar matriculas.
- `yolov8n.pt` es un modelo COCO general usado como contexto para detectar vehiculos y filtrar falsos positivos de matriculas.
- Los modelos YOLO generales entrenados con COCO no suelen servir como unica solucion porque no incluyen matriculas ni caras como clases especificas.
- Los pesos `.pt` de esta carpeta forman parte del repositorio si se decide distribuir esta version ya preparada.

## Modelos recomendados para uso interno

Para esta version se recomienda:

- Caras: `lindevs/yolov8-face`, modelo `yolov8n-face-lindevs.pt`, licencia declarada MIT.
- Matriculas: `Koushim/yolov8-license-plate-detection`, archivo `best.pt`, licencia declarada MIT.
- Vehiculos: `yolov8n.pt` de Ultralytics, clases COCO, licencia declarada AGPL-3.0.

Puedes descargarlos con:

```bash
python models/download_models.py
```

El script los guarda como:

```text
models/yolo_faces.pt
models/yolo_plates.pt
models/yolov8n.pt
```

Tambien crea `models/MODELS_DOWNLOADED.md` con origen, licencia declarada y fecha de descarga.

Esta seleccion se ha hecho para uso interno. Si la herramienta se distribuye fuera de la organizacion o se comercializa, conviene revisar de nuevo las licencias de librerias y modelos.
