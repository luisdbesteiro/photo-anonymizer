# Modelos YOLO

Coloca aqui los modelos YOLO preentrenados:

```text
models/yolo_faces.pt
models/yolo_plates.pt
```

Importante:

- `yolo_faces.pt` debe estar entrenado para detectar caras.
- `yolo_plates.pt` debe estar entrenado para detectar matriculas.
- Los modelos YOLO generales entrenados con COCO, como `yolov8n.pt`, no suelen servir para este caso porque no incluyen matriculas ni caras como clases especificas.
- Los pesos `.pt` de esta carpeta forman parte del repositorio si se decide distribuir esta version ya preparada.

## Modelos recomendados para uso interno

Para esta version se recomienda:

- Caras: `lindevs/yolov8-face`, modelo `yolov8n-face-lindevs.pt`, licencia declarada MIT.
- Matriculas: `Koushim/yolov8-license-plate-detection`, archivo `best.pt`, licencia declarada MIT.

Puedes descargarlos con:

```bash
python models/download_models.py
```

El script los guarda como:

```text
models/yolo_faces.pt
models/yolo_plates.pt
```

Tambien crea `models/MODELS_DOWNLOADED.md` con origen, licencia declarada y fecha de descarga.

Esta seleccion se ha hecho para uso interno. Si la herramienta se distribuye fuera de la organizacion o se comercializa, conviene revisar de nuevo las licencias de librerias y modelos.
