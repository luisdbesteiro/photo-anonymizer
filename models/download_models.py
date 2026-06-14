#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


@dataclass(frozen=True)
class ModelInfo:
    name: str
    output_name: str
    url: str
    source: str
    license_name: str
    notes: str
    sha256: str | None = None


MODELS = [
    ModelInfo(
        name="caras",
        output_name="yolo_faces.pt",
        url="https://huggingface.co/iitolstykh/YOLO-Face-Person-Detector/resolve/main/yolov8x_person_face.pt",
        source="https://huggingface.co/iitolstykh/YOLO-Face-Person-Detector",
        license_name="AGPL-3.0",
        notes=(
            "Modelo YOLOv8x para deteccion de caras y personas. "
            "La aplicacion filtra solo la clase face para anonimizar caras."
        ),
    ),
    ModelInfo(
        name="matriculas",
        output_name="yolo_plates.pt",
        url="https://huggingface.co/Koushim/yolov8-license-plate-detection/resolve/main/best.pt",
        source="https://huggingface.co/Koushim/yolov8-license-plate-detection",
        license_name="MIT",
        notes="Modelo YOLOv8 para deteccion de matriculas. Uso previsto: herramienta interna.",
    ),
    ModelInfo(
        name="vehiculos",
        output_name="yolov8n.pt",
        url="https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.pt",
        source="https://github.com/ultralytics/assets",
        license_name="AGPL-3.0",
        notes="Modelo COCO YOLOv8n usado solo como contexto para validar que una matricula detectada pertenece a un vehiculo.",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Descarga los modelos YOLO recomendados para uso interno.")
    parser.add_argument("--models-dir", help="Carpeta donde guardar los modelos. Por defecto: esta carpeta.")
    parser.add_argument("--force", action="store_true", help="Vuelve a descargar aunque el archivo exista.")
    parser.add_argument("--list", action="store_true", help="Muestra los modelos configurados sin descargarlos.")
    parser.add_argument(
        "--only",
        choices=[model.name for model in MODELS],
        action="append",
        help="Descarga solo el modelo indicado. Se puede repetir. Ejemplo: --only caras",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    models_dir = Path(args.models_dir) if args.models_dir else Path(__file__).resolve().parent

    selected_models = [model for model in MODELS if not args.only or model.name in args.only]

    if args.list:
        for model in selected_models:
            print(f"{model.name}: {model.output_name}")
            print(f"  Origen: {model.source}")
            print(f"  Licencia declarada: {model.license_name}")
            print(f"  URL: {model.url}")
        return 0

    models_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[ModelInfo] = []

    for model in selected_models:
        destination = models_dir / model.output_name
        if destination.exists() and not args.force:
            print(f"Ya existe {destination}. Usa --force para descargarlo de nuevo.")
            downloaded.append(model)
            continue

        try:
            print(f"Descargando modelo de {model.name}...")
            _download_file(model.url, destination)
            if model.sha256:
                _verify_sha256(destination, model.sha256)
            print(f"Guardado: {destination}")
            downloaded.append(model)
        except Exception as exc:
            if destination.exists():
                destination.unlink()
            print(f"Error descargando {model.name}: {exc}")
            return 1

    _write_manifest(models_dir, downloaded)
    print()
    print("Modelos listos.")
    print("Puedes ejecutar run_app.bat en Windows o run_app_linux.sh en Ubuntu.")
    return 0


def _download_file(url: str, destination: Path) -> None:
    try:
        with urlopen(url, timeout=60) as response:
            total = int(response.headers.get("Content-Length", "0"))
            downloaded = 0
            with destination.open("wb") as file:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = downloaded * 100 / total
                        print(f"  {percent:5.1f}%", end="\r")
            print(" " * 20, end="\r")
    except URLError as exc:
        raise RuntimeError("No se pudo conectar con el servidor de descarga.") from exc


def _verify_sha256(path: Path, expected: str) -> None:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual.lower() != expected.lower():
        raise ValueError(f"SHA-256 inesperado para {path.name}. Esperado {expected}, obtenido {actual}.")


def _write_manifest(models_dir: Path, models: list[ModelInfo]) -> None:
    lines = [
        "# Modelos descargados",
        "",
        f"Fecha: {date.today().isoformat()}",
        "",
    ]
    for model in models:
        lines.extend(
            [
                f"## {model.output_name}",
                "",
                f"- Uso: {model.name}",
                f"- Origen: {model.source}",
                f"- URL de descarga: {model.url}",
                f"- Licencia declarada por la fuente: {model.license_name}",
                f"- Notas: {model.notes}",
                "",
            ]
        )
    (models_dir / "MODELS_DOWNLOADED.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
