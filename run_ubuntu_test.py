#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import logging
import sys
import traceback
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

from src.anonymizer import Box
from src.anonymizer import anonymize_regions
from src.detector_faces import detect_faces
from src.detector_plates import detect_plates
from src.detector_faces import MIN_FACE_CONFIDENCE
from src.detector_plates import MIN_CONTEXT_PLATE_CONFIDENCE, MIN_STANDALONE_PLATE_CONFIDENCE
from src.utils import collect_images, make_output_path, read_image, setup_logging, write_image
from src.yolo_detector import (
    DEFAULT_FACE_MODEL,
    DEFAULT_PLATE_MODEL,
    DEFAULT_VEHICLE_MODEL,
    Detection,
    check_yolo_ready,
    detect_with_yolo_details,
)


DiagnosticDetection = tuple[str, Detection]
COCO_VEHICLE_CLASSES = {"bicycle", "car", "motorcycle", "bus", "truck"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prueba en Ubuntu la deteccion y anonimizacion sin abrir la interfaz grafica."
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        default=["fotos"],
        help="Imagenes o carpetas de entrada. Por defecto: fotos",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output_ubuntu_test",
        help="Carpeta de salida. Por defecto: output_ubuntu_test",
    )
    parser.add_argument(
        "-m",
        "--method",
        choices=["desenfoque", "pixelado", "negro"],
        default="desenfoque",
        help="Metodo de anonimizacion. Por defecto: desenfoque",
    )
    parser.add_argument("--no-faces", action="store_true", help="No detectar caras.")
    parser.add_argument("--no-plates", action="store_true", help="No detectar matriculas.")
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="No anonimiza. Dibuja todas las clases detectadas por los modelos seleccionados.",
    )
    parser.add_argument(
        "--diagnostic-models",
        choices=["all", "faces", "plates", "vehicles"],
        default="all",
        help="Modelos a ejecutar en modo diagnostico. Por defecto: all.",
    )
    parser.add_argument(
        "--plate-imgsz",
        type=int,
        default=1600,
        help="Tamano de inferencia para diagnostico del modelo de matriculas. Por defecto: 1600.",
    )
    parser.add_argument(
        "--vehicle-imgsz",
        type=int,
        default=1280,
        help="Tamano de inferencia para diagnostico del modelo COCO/vehiculos. Por defecto: 1280.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Procesa solo las primeras N imagenes. 0 significa sin limite.",
    )
    parser.add_argument(
        "--face-model",
        default=str(DEFAULT_FACE_MODEL),
        help="Ruta al modelo YOLO de caras. Por defecto: models/yolo_faces.pt",
    )
    parser.add_argument(
        "--plate-model",
        default=str(DEFAULT_PLATE_MODEL),
        help="Ruta al modelo YOLO de matriculas. Por defecto: models/yolo_plates.pt",
    )
    parser.add_argument(
        "--vehicle-model",
        default=str(DEFAULT_VEHICLE_MODEL),
        help="Ruta al modelo YOLO de vehiculos usado como contexto. Por defecto: models/yolov8n.pt",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=MIN_FACE_CONFIDENCE,
        help=(
            "Confianza minima solicitada entre 0 y 1 para modo normal. "
            f"La prueba no baja de {MIN_STANDALONE_PLATE_CONFIDENCE} en matriculas directas."
        ),
    )
    parser.add_argument(
        "--diagnostic-face-confidence",
        type=float,
        default=0.6,
        help="Confianza minima para caras en modo diagnostico. Por defecto: 0.6.",
    )
    parser.add_argument(
        "--diagnostic-plate-confidence",
        type=float,
        default=0.4,
        help="Confianza minima para matriculas en modo diagnostico. Por defecto: 0.4.",
    )
    parser.add_argument(
        "--diagnostic-vehicle-confidence",
        type=float,
        default=0.2,
        help="Confianza minima para vehiculos en modo diagnostico. Por defecto: 0.2.",
    )
    parser.add_argument(
        "--plate-context-confidence",
        type=float,
        default=MIN_CONTEXT_PLATE_CONFIDENCE,
        help=(
            "Confianza minima para aceptar matriculas con contexto de vehiculo. "
            f"Por defecto: {MIN_CONTEXT_PLATE_CONFIDENCE}."
        ),
    )
    parser.add_argument(
        "--draw-detections",
        action="store_true",
        help="Dibuja cajas y etiquetas sobre las zonas detectadas en las imagenes guardadas.",
    )
    return parser.parse_args()


def main() -> int:
    project_root = Path(__file__).resolve().parent
    setup_logging(project_root)
    args = parse_args()

    detect_faces_enabled = not args.no_faces
    detect_plates_enabled = not args.no_plates
    if not args.diagnostic and not detect_faces_enabled and not detect_plates_enabled:
        print("Activa caras, matriculas o ambas detecciones.")
        return 2

    face_model = Path(args.face_model).expanduser()
    plate_model = Path(args.plate_model).expanduser()
    vehicle_model = Path(args.vehicle_model).expanduser()
    required_models = []
    if args.diagnostic:
        if args.diagnostic_models in {"all", "faces"}:
            required_models.append(face_model)
        if args.diagnostic_models in {"all", "plates"}:
            required_models.append(plate_model)
        if args.diagnostic_models in {"all", "vehicles"}:
            required_models.append(vehicle_model)
    else:
        if detect_faces_enabled:
            required_models.append(face_model)
        if detect_plates_enabled:
            required_models.append(plate_model)
            required_models.append(vehicle_model)

    try:
        check_yolo_ready(required_models)
    except Exception as exc:
        print(exc)
        return 2

    input_paths = [Path(item).expanduser() for item in args.input]
    images = collect_images(input_paths)
    if args.limit > 0:
        images = images[: args.limit]

    if not images:
        print("No se encontraron imagenes compatibles.")
        print("Formatos soportados: jpg, jpeg, png, bmp, tif, tiff, webp")
        return 1

    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    errors = 0
    total_faces = 0
    total_plates = 0
    diagnostic_rows: list[dict[str, object]] = []

    print(f"Imagenes encontradas: {len(images)}")
    print(f"Salida: {output_dir.resolve()}")
    if args.diagnostic:
        print(f"Modo: diagnostico ({args.diagnostic_models})")
        print(
            "Confianzas: "
            f"caras>{args.diagnostic_face_confidence}, "
            f"matriculas>{args.diagnostic_plate_confidence}, "
            f"vehiculos>{args.diagnostic_vehicle_confidence}"
        )
    else:
        print(f"Metodo: {args.method}")
    print()

    for index, image_path in enumerate(images, start=1):
        try:
            image = read_image(image_path)
            if image is None:
                raise ValueError("No se pudo abrir la imagen.")

            if args.diagnostic:
                diagnostic_detections = run_diagnostic_detection(
                    image,
                    args,
                    face_model,
                    plate_model,
                    vehicle_model,
                )
                diagnostic_rows.extend(build_diagnostic_rows(image_path, diagnostic_detections))
                output_image = draw_diagnostic_detections(image, diagnostic_detections)
                output_path = make_output_path(image_path, output_dir, suffix="_diagnostico")
                if not write_image(output_path, output_image, source_path=image_path):
                    raise ValueError("No se pudo guardar la imagen procesada.")

                processed += 1
                class_counts = count_diagnostic_classes(diagnostic_detections)
                print(
                    f"[{index}/{len(images)}] OK {image_path.name} -> {output_path.name} "
                    f"({format_class_counts(class_counts)})"
                )
                logging.info(
                    "Diagnostico %s -> %s. Detecciones=%s",
                    image_path,
                    output_path,
                    dict(class_counts),
                )
                continue

            boxes = []
            face_boxes = []
            plate_boxes = []
            face_count = 0
            plate_count = 0

            if detect_faces_enabled:
                face_boxes = detect_faces(image, face_model, args.confidence)
                boxes.extend(face_boxes)
                face_count = len(face_boxes)

            if detect_plates_enabled:
                plate_boxes = detect_plates(
                    image,
                    plate_model,
                    max(args.confidence, MIN_STANDALONE_PLATE_CONFIDENCE),
                    vehicle_model,
                    context_confidence=args.plate_context_confidence,
                )
                boxes.extend(plate_boxes)
                plate_count = len(plate_boxes)

            anonymized = anonymize_regions(image, boxes, args.method)
            if args.draw_detections:
                anonymized = draw_detections(anonymized, face_boxes, plate_boxes)

            output_path = make_output_path(image_path, output_dir)
            if not write_image(output_path, anonymized, source_path=image_path):
                raise ValueError("No se pudo guardar la imagen procesada.")

            processed += 1
            total_faces += face_count
            total_plates += plate_count
            print(
                f"[{index}/{len(images)}] OK {image_path.name} -> {output_path.name} "
                f"(caras: {face_count}, matriculas: {plate_count})"
            )
            logging.info(
                "Ubuntu test procesada %s -> %s. Caras=%s Matriculas=%s",
                image_path,
                output_path,
                face_count,
                plate_count,
            )
        except Exception as exc:
            errors += 1
            print(f"[{index}/{len(images)}] ERROR {image_path}: {exc}")
            logging.error("Error procesando %s: %s\n%s", image_path, exc, traceback.format_exc())

    print()
    print("Resumen")
    print(f"Imagenes procesadas: {processed}")
    print(f"Errores: {errors}")
    if not args.diagnostic:
        print(f"Caras detectadas: {total_faces}")
        print(f"Matriculas detectadas: {total_plates}")
    elif diagnostic_rows:
        csv_path = output_dir / "detecciones_diagnostico.csv"
        write_diagnostic_csv(csv_path, diagnostic_rows)
        print(f"CSV de detecciones: {csv_path.resolve()}")
    print(f"Carpeta de salida: {output_dir.resolve()}")
    if args.diagnostic:
        print("Revisa las cajas y etiquetas para localizar errores de clasificacion.")
    else:
        print("Revisa las imagenes generadas antes de compartirlas.")

    return 0 if errors == 0 else 1


def run_diagnostic_detection(
    image: np.ndarray,
    args: argparse.Namespace,
    face_model: Path,
    plate_model: Path,
    vehicle_model: Path,
) -> list[DiagnosticDetection]:
    detections: list[DiagnosticDetection] = []
    if args.diagnostic_models in {"all", "faces"}:
        detections.extend(
            ("caras", detection)
            for detection in detect_with_yolo_details(image, face_model, args.diagnostic_face_confidence)
        )
    if args.diagnostic_models in {"all", "plates"}:
        detections.extend(
            ("matriculas", detection)
            for detection in detect_with_yolo_details(
                image,
                plate_model,
                args.diagnostic_plate_confidence,
                image_size=args.plate_imgsz,
            )
        )
    if args.diagnostic_models in {"all", "vehicles"}:
        detections.extend(
            ("coco", detection)
            for detection in detect_with_yolo_details(
                image,
                vehicle_model,
                args.diagnostic_vehicle_confidence,
                class_names=COCO_VEHICLE_CLASSES,
                image_size=args.vehicle_imgsz,
            )
        )
    return detections


def build_diagnostic_rows(image_path: Path, detections: list[DiagnosticDetection]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source, detection in detections:
        x, y, w, h, score, class_name = detection
        rows.append(
            {
                "image": str(image_path),
                "model": source,
                "class": class_name,
                "confidence": round(score, 6),
                "x": x,
                "y": y,
                "w": w,
                "h": h,
            }
        )
    return rows


def write_diagnostic_csv(csv_path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = ["image", "model", "class", "confidence", "x", "y", "w", "h"]
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def draw_diagnostic_detections(image: np.ndarray, detections: list[DiagnosticDetection]) -> np.ndarray:
    result = image.copy()
    for source, detection in detections:
        x, y, w, h, score, class_name = detection
        label = f"{source}:{class_name} {score:.2f}"
        _draw_box(result, (x, y, w, h), label, _color_for_source(source))
    return result


def count_diagnostic_classes(detections: list[DiagnosticDetection]) -> Counter[str]:
    return Counter(f"{source}:{detection[5]}" for source, detection in detections)


def format_class_counts(class_counts: Counter[str]) -> str:
    if not class_counts:
        return "sin detecciones"
    return ", ".join(f"{name}: {count}" for name, count in sorted(class_counts.items()))


def draw_detections(image: np.ndarray, face_boxes: list[Box], plate_boxes: list[Box]) -> np.ndarray:
    result = image.copy()
    for box in face_boxes:
        _draw_box(result, box, "cara", (0, 180, 0))
    for box in plate_boxes:
        _draw_box(result, box, "matricula", (255, 80, 0))
    return result


def _color_for_source(source: str) -> tuple[int, int, int]:
    if source == "caras":
        return (0, 180, 0)
    if source == "matriculas":
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


if __name__ == "__main__":
    sys.exit(main())
