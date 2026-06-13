from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, PngImagePlugin


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
EXIF_ORIENTATION_TAG = 274


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
    return _default_sibling_dir_for_paths(paths, fallback, "_anonimizadas")


def default_annotated_dir_for_paths(paths: list[Path], fallback: Path) -> Path:
    return _default_sibling_dir_for_paths(paths, fallback, "_anotadas")


def _default_sibling_dir_for_paths(paths: list[Path], fallback: Path, suffix: str) -> Path:
    if not paths:
        return fallback

    first_path = paths[0]
    input_dir = first_path if first_path.is_dir() else first_path.parent
    if not input_dir.name:
        return fallback

    return input_dir.parent / f"{input_dir.name}{suffix}"


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


def write_image(path: Path, image: np.ndarray, source_path: Path | None = None) -> bool:
    if source_path is not None:
        try:
            _write_image_with_metadata(path, image, source_path)
            return True
        except Exception as exc:
            logging.warning(
                "No se pudieron copiar los metadatos de %s a %s: %s. Se guarda sin metadatos.",
                source_path,
                path,
                exc,
            )

    extension = path.suffix.lower() or ".jpg"
    ok, encoded = cv2.imencode(extension, image)
    if not ok:
        return False
    encoded.tofile(str(path))
    return True


def _write_image_with_metadata(path: Path, image: np.ndarray, source_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pil_image = _cv_image_to_pillow(image)
    extension = path.suffix.lower() or ".jpg"
    image_format = _pillow_format_for_extension(extension)
    save_kwargs = _metadata_save_kwargs(source_path, extension)

    if image_format == "JPEG" and pil_image.mode not in {"RGB", "L"}:
        pil_image = pil_image.convert("RGB")
    if image_format in {"JPEG", "WEBP"}:
        save_kwargs.setdefault("quality", 95)

    pil_image.save(path, format=image_format, **save_kwargs)


def _cv_image_to_pillow(image: np.ndarray) -> Image.Image:
    if image.ndim == 2:
        return Image.fromarray(image)
    if image.shape[2] == 4:
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA))
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def _pillow_format_for_extension(extension: str) -> str:
    formats = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".bmp": "BMP",
        ".tif": "TIFF",
        ".tiff": "TIFF",
        ".webp": "WEBP",
    }
    return formats.get(extension.lower(), extension.lstrip(".").upper() or "JPEG")


def _metadata_save_kwargs(source_path: Path, extension: str) -> dict[str, object]:
    with Image.open(source_path) as source:
        info = dict(source.info)
        save_kwargs: dict[str, object] = {}

        exif = source.getexif()
        if exif:
            exif[EXIF_ORIENTATION_TAG] = 1
            save_kwargs["exif"] = exif.tobytes()
        elif "exif" in info:
            save_kwargs["exif"] = info["exif"]

        if info.get("icc_profile"):
            save_kwargs["icc_profile"] = info["icc_profile"]
        if info.get("dpi"):
            save_kwargs["dpi"] = info["dpi"]

        if extension.lower() == ".png":
            pnginfo = _png_text_metadata(info)
            if pnginfo:
                save_kwargs["pnginfo"] = pnginfo

        return save_kwargs


def _png_text_metadata(info: dict[str, object]) -> PngImagePlugin.PngInfo | None:
    pnginfo = PngImagePlugin.PngInfo()
    has_text = False
    reserved_keys = {"exif", "icc_profile", "dpi", "transparency", "gamma"}
    for key, value in info.items():
        if key in reserved_keys:
            continue
        if isinstance(value, str):
            pnginfo.add_text(key, value)
            has_text = True
        elif isinstance(value, bytes):
            try:
                pnginfo.add_text(key, value.decode("utf-8"))
                has_text = True
            except UnicodeDecodeError:
                continue
    return pnginfo if has_text else None


def _deduplicate(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(path)
    return result
