from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def setup_logging(project_root: Path) -> None:
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_dir / "anonimizador.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


def collect_images(paths: list[Path]) -> list[Path]:
    images: list[Path] = []
    for path in paths:
        if path.is_dir():
            images.extend(
                sorted(
                    child
                    for child in path.rglob("*")
                    if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS
                )
            )
        elif path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            images.append(path)
    return _deduplicate(images)


def default_output_dir_for_paths(paths: list[Path], fallback: Path) -> Path:
    if not paths:
        return fallback

    first_path = paths[0]
    input_dir = first_path if first_path.is_dir() else first_path.parent
    if not input_dir.name:
        return fallback

    return input_dir.parent / f"{input_dir.name}_anonimizadas"


def make_output_path(input_path: Path, output_dir: Path, suffix: str = "_anonimizada") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    extension = input_path.suffix.lower() if input_path.suffix else ".jpg"
    candidate = output_dir / f"{input_path.stem}{suffix}{extension}"
    counter = 2
    while candidate.exists():
        candidate = output_dir / f"{input_path.stem}{suffix}_{counter}{extension}"
        counter += 1
    return candidate


def read_image(path: Path) -> np.ndarray | None:
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def write_image(path: Path, image: np.ndarray) -> bool:
    extension = path.suffix.lower() or ".jpg"
    ok, encoded = cv2.imencode(extension, image)
    if not ok:
        return False
    encoded.tofile(str(path))
    return True


def _deduplicate(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(path)
    return result
