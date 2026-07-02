from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import numpy as np

from .anonymizer import Box


DEFAULT_FACE_MODEL = Path("models/yolo_faces.pt")
DEFAULT_PLATE_MODEL = Path("models/yolo_plates.pt")
DEFAULT_VEHICLE_MODEL = Path("models/yolov8n.pt")
Detection = tuple[int, int, int, int, float, str]


def detect_with_yolo(
    image: np.ndarray,
    model_path: Path,
    confidence: float = 0.35,
    class_names: set[str] | None = None,
) -> list[Box]:
    detections = detect_with_yolo_details(image, model_path, confidence, class_names=class_names)
    return [(x, y, w, h) for x, y, w, h, _score, _name in detections]


def detect_with_yolo_details(
    image: np.ndarray,
    model_path: Path,
    confidence: float = 0.35,
    class_names: set[str] | None = None,
    image_size: int | None = None,
) -> list[Detection]:
    model_path = model_path.expanduser()
    if not model_path.exists():
        raise FileNotFoundError(f"No se encontro el modelo YOLO: {model_path}")

    model = _load_model(str(model_path.resolve()))
    predict_args = {"conf": confidence, "verbose": False}
    if image_size:
        predict_args["imgsz"] = image_size
    results = model.predict(image, **predict_args)

    detections: list[Detection] = []
    for result in results:
        if result.boxes is None:
            continue
        names = result.names or {}
        xyxy = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        scores = result.boxes.conf.cpu().numpy()
        for item, class_id, score in zip(xyxy, classes, scores):
            detected_name = str(names.get(class_id, class_id)).lower()
            if class_names and detected_name not in class_names:
                continue

            x1, y1, x2, y2 = item[:4]
            x = int(round(x1))
            y = int(round(y1))
            w = int(round(x2 - x1))
            h = int(round(y2 - y1))
            if w > 0 and h > 0:
                detections.append((x, y, w, h, float(score), detected_name))
    return detections


def check_yolo_ready(model_paths: list[Path]) -> None:
    missing = [str(path) for path in model_paths if not path.expanduser().exists()]
    if missing:
        raise FileNotFoundError(
            "Faltan modelos YOLO:\n"
            + "\n".join(f"- {path}" for path in missing)
            + "\n\nCopia los modelos preentrenados en la carpeta models/."
        )

    _ensure_ultralytics_config_dir()

    try:
        import ultralytics  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Falta la dependencia ultralytics. Ejecuta ./run_app.sh o ./installer_scripts/install_linux.sh."
        ) from exc


@lru_cache(maxsize=4)
def _load_model(model_path: str):
    _ensure_ultralytics_config_dir()

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            "Falta la dependencia ultralytics. Ejecuta ./run_app.sh o ./installer_scripts/install_linux.sh."
        ) from exc

    return YOLO(model_path)


def _ensure_ultralytics_config_dir() -> None:
    project_root = Path(__file__).resolve().parents[1]
    config_dir = project_root / "logs" / "ultralytics"
    config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(config_dir))
