from __future__ import annotations

import cv2
import numpy as np


Box = tuple[int, int, int, int]


def clamp_box(box: Box, image_shape: tuple[int, ...], padding: int = 0) -> Box | None:
    x, y, w, h = box
    height, width = image_shape[:2]
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width, x + w + padding)
    y2 = min(height, y + h + padding)
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2 - x1, y2 - y1


def anonymize_regions(image: np.ndarray, boxes: list[Box], method: str) -> np.ndarray:
    result = image.copy()
    for box in boxes:
        safe_box = clamp_box(box, result.shape, padding=8)
        if safe_box is None:
            continue

        x, y, w, h = safe_box
        region = result[y : y + h, x : x + w]
        if region.size == 0:
            continue

        if method == "pixelado":
            result[y : y + h, x : x + w] = _pixelate(region)
        elif method == "negro":
            result[y : y + h, x : x + w] = 0
        else:
            result[y : y + h, x : x + w] = _strong_blur(region)

    return result


def _strong_blur(region: np.ndarray) -> np.ndarray:
    min_side = max(3, min(region.shape[:2]))
    kernel = max(61, min_side | 1)
    blurred = cv2.GaussianBlur(region, (kernel, kernel), 0)
    return cv2.GaussianBlur(blurred, (kernel, kernel), 0)


def _pixelate(region: np.ndarray) -> np.ndarray:
    height, width = region.shape[:2]
    small_width = max(1, width // 18)
    small_height = max(1, height // 18)
    small = cv2.resize(region, (small_width, small_height), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)
