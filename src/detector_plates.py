from __future__ import annotations

import numpy as np

from .anonymizer import Box
from .yolo_detector import DEFAULT_PLATE_MODEL, DEFAULT_VEHICLE_MODEL, Detection, detect_with_yolo_details


PLATE_CLASS_NAMES = {"license-plate", "licence-plate", "plate", "license_plate", "licence_plate"}
VEHICLE_CLASS_NAMES = {"car", "motorcycle", "bus", "truck"}
PLATE_IMAGE_SIZE = 1600
VEHICLE_IMAGE_SIZE = 1280
RAW_CONFIDENCE = 0.01
MIN_CONTEXT_PLATE_CONFIDENCE = 0.20
MIN_STANDALONE_PLATE_CONFIDENCE = 0.90
MIN_VEHICLE_CONFIDENCE = 0.25


def detect_plates(
    image: np.ndarray,
    model_path=DEFAULT_PLATE_MODEL,
    confidence: float = MIN_STANDALONE_PLATE_CONFIDENCE,
    vehicle_model_path=DEFAULT_VEHICLE_MODEL,
    context_confidence: float = MIN_CONTEXT_PLATE_CONFIDENCE,
    vehicle_confidence: float = MIN_VEHICLE_CONFIDENCE,
) -> list[Box]:
    plate_detections = detect_with_yolo_details(image, model_path, RAW_CONFIDENCE, image_size=PLATE_IMAGE_SIZE)

    plate_boxes: list[Box] = []
    context_candidates: list[Detection] = []
    for detection in plate_detections:
        x, y, w, h, score, class_name = detection
        if class_name not in PLATE_CLASS_NAMES:
            continue
        if not _looks_like_plate((x, y, w, h), image.shape):
            continue
        if _looks_like_timestamp_overlay((x, y, w, h), image.shape):
            continue
        if score >= max(confidence, RAW_CONFIDENCE):
            plate_boxes.append((x, y, w, h))
            continue
        if score >= max(context_confidence, RAW_CONFIDENCE):
            context_candidates.append(detection)

    if context_candidates:
        vehicle_boxes = detect_with_yolo_details(
            image,
            vehicle_model_path,
            max(vehicle_confidence, RAW_CONFIDENCE),
            class_names=VEHICLE_CLASS_NAMES,
            image_size=VEHICLE_IMAGE_SIZE,
        )
        for detection in context_candidates:
            if _has_vehicle_context(detection, vehicle_boxes):
                x, y, w, h, _score, _class_name = detection
                plate_boxes.append((x, y, w, h))

    return _deduplicate_boxes(plate_boxes)


def _looks_like_plate(box: Box, image_shape: tuple[int, ...]) -> bool:
    x, y, w, h = box
    image_height, image_width = image_shape[:2]
    image_area = image_width * image_height
    box_area = w * h
    if image_area <= 0 or box_area <= 0:
        return False

    aspect_ratio = w / h
    area_ratio = box_area / image_area
    width_ratio = w / image_width
    height_ratio = h / image_height

    if aspect_ratio < 1.8 or aspect_ratio > 8.0:
        return False
    if area_ratio < 0.00002 or area_ratio > 0.012:
        return False
    if width_ratio > 0.30 or height_ratio > 0.12:
        return False
    if y + h < image_height * 0.12:
        return False

    return True


def _looks_like_timestamp_overlay(box: Box, image_shape: tuple[int, ...]) -> bool:
    x, y, w, h = box
    image_height, image_width = image_shape[:2]
    return x > image_width * 0.55 and y + h > image_height * 0.94


def _has_vehicle_context(plate: Detection, vehicles: list[Detection]) -> bool:
    if not vehicles:
        return False

    px, py, pw, ph, _score, _name = plate
    center_x = px + pw / 2
    center_y = py + ph / 2
    for vehicle in vehicles:
        vx, vy, vw, vh, _vehicle_score, _vehicle_name = vehicle
        margin_x = max(10, vw * 0.08)
        margin_y = max(10, vh * 0.12)
        if (
            vx - margin_x <= center_x <= vx + vw + margin_x
            and vy - margin_y <= center_y <= vy + vh + margin_y
        ):
            return True
    return False


def _deduplicate_boxes(boxes: list[Box]) -> list[Box]:
    selected: list[Box] = []
    for box in boxes:
        if all(_intersection_over_union(box, existing) < 0.35 for existing in selected):
            selected.append(box)
    return selected


def _intersection_over_union(first: Box, second: Box) -> float:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    ax2 = ax + aw
    ay2 = ay + ah
    bx2 = bx + bw
    by2 = by + bh

    ix1 = max(ax, bx)
    iy1 = max(ay, by)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    intersection = (ix2 - ix1) * (iy2 - iy1)
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0 else 0.0
