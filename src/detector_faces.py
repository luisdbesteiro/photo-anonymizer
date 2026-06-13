from __future__ import annotations

import numpy as np

from .anonymizer import Box
from .yolo_detector import DEFAULT_FACE_MODEL, detect_with_yolo

MIN_FACE_CONFIDENCE = 0.70


def detect_faces(image: np.ndarray, model_path=DEFAULT_FACE_MODEL, confidence: float = MIN_FACE_CONFIDENCE) -> list[Box]:
    effective_confidence = max(confidence, MIN_FACE_CONFIDENCE)
    return detect_with_yolo(image, model_path, effective_confidence)
