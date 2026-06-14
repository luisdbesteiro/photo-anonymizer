from __future__ import annotations

import cv2
import numpy as np

from .anonymizer import Box
from .yolo_detector import Detection


def draw_detections(image: np.ndarray, face_boxes: list[Box], plate_boxes: list[Box]) -> np.ndarray:
    result = image.copy()
    for box in face_boxes:
        _draw_box(result, box, "cara", (0, 180, 0))
    for box in plate_boxes:
        _draw_box(result, box, "matricula", (255, 80, 0))
    return result


def draw_debug_detections(image: np.ndarray, detections: list[tuple[str, Detection]]) -> np.ndarray:
    result = image.copy()
    for source, detection in detections:
        x, y, w, h, score, class_name = detection
        label = f"{source}:{class_name} {score:.2f}"
        _draw_box(result, (x, y, w, h), label, _color_for_source(source))
    return result


def _color_for_source(source: str) -> tuple[int, int, int]:
    if source == "cara":
        return (0, 180, 0)
    if source == "matricula":
        return (255, 80, 0)
    return (0, 120, 255)


def _draw_box(image: np.ndarray, box: Box, label: str, color: tuple[int, int, int]) -> None:
    x, y, w, h = box
    x1 = max(0, int(x))
    y1 = max(0, int(y))
    x2 = min(image.shape[1] - 1, int(x + w))
    y2 = min(image.shape[0] - 1, int(y + h))
    if x2 <= x1 or y2 <= y1:
        return

    thickness = max(2, min(image.shape[:2]) // 350)
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

    font_scale = max(0.5, min(image.shape[:2]) / 1400)
    text_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    text_width, text_height = text_size
    label_y1 = max(0, y1 - text_height - baseline - 6)
    label_y2 = min(image.shape[0] - 1, label_y1 + text_height + baseline + 6)
    label_x2 = min(image.shape[1] - 1, x1 + text_width + 8)
    cv2.rectangle(image, (x1, label_y1), (label_x2, label_y2), color, -1)
    cv2.putText(
        image,
        label,
        (x1 + 4, label_y2 - baseline - 3),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )
