from __future__ import annotations

import numpy as np

from .anonymizer import Box
from .yolo_detector import DEFAULT_FACE_MODEL, detect_with_yolo

FACE_CLASS_NAMES = {"face"}
MIN_FACE_CONFIDENCE = 0.10


def detect_faces(image: np.ndarray, model_path=DEFAULT_FACE_MODEL, confidence: float = MIN_FACE_CONFIDENCE) -> list[Box]:
    effective_confidence = max(confidence, 0.01)
    return detect_with_yolo(image, model_path, effective_confidence, class_names=FACE_CLASS_NAMES)
