from __future__ import annotations

import logging
import threading
import traceback
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .anonymizer import anonymize_regions
from .debug_drawing import draw_debug_detections
from .detector_faces import FACE_CLASS_NAMES, MIN_FACE_CONFIDENCE, detect_faces
from .detector_plates import (
    MIN_CONTEXT_PLATE_CONFIDENCE,
    MIN_STANDALONE_PLATE_CONFIDENCE,
    MIN_VEHICLE_CONFIDENCE,
    PLATE_CLASS_NAMES,
    PLATE_IMAGE_SIZE,
    VEHICLE_CLASS_NAMES,
    VEHICLE_IMAGE_SIZE,
    detect_plates,
)
from .utils import (
    collect_images,
    default_annotated_dir_for_paths,
    default_output_dir_for_paths,
    make_output_path,
    read_image,
    write_image,
)
from .yolo_detector import (
    DEFAULT_FACE_MODEL,
    DEFAULT_PLATE_MODEL,
    DEFAULT_VEHICLE_MODEL,
    Detection,
    check_yolo_ready,
    detect_with_yolo_details,
)


@dataclass
class ProcessResult:
    processed: int = 0
    errors: int = 0
    faces: int = 0
    plates: int = 0


MIN_SLIDER_CONFIDENCE = 0.01


class AnonymizerApp(tk.Tk):
    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.project_root = project_root
        self.selected_paths: list[Path] = []

        self.title("Anonimizador de caras y matriculas")
        self.geometry("760x560")
        self.minsize(680, 500)

        self.output_dir = tk.StringVar(value=str(project_root / "output"))
        self.method = tk.StringVar(value="desenfoque")
        self.detect_faces_enabled = tk.BooleanVar(value=True)
        self.detect_plates_enabled = tk.BooleanVar(value=True)
        self.save_annotated_debug = tk.BooleanVar(value=False)
        self.show_confidence_options = tk.BooleanVar(value=False)
        self.face_confidence = tk.DoubleVar(value=MIN_FACE_CONFIDENCE)
        self.plate_confidence = tk.DoubleVar(value=MIN_STANDALONE_PLATE_CONFIDENCE)
        self.plate_context_confidence = tk.DoubleVar(value=MIN_CONTEXT_PLATE_CONFIDENCE)
        self.vehicle_confidence = tk.DoubleVar(value=MIN_VEHICLE_CONFIDENCE)
        self.face_model_path = project_root / DEFAULT_FACE_MODEL
        self.plate_model_path = project_root / DEFAULT_PLATE_MODEL
        self.vehicle_model_path = project_root / DEFAULT_VEHICLE_MODEL
        self.status = tk.StringVar(value="Selecciona imagenes o una carpeta para empezar.")
        self.progress = tk.DoubleVar(value=0)

        self._build_ui()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        title = ttk.Label(root, text="Anonimizador de caras y matriculas", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 12))

        controls = ttk.Frame(root)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        for column in range(3):
            controls.columnconfigure(column, weight=1)

        ttk.Button(controls, text="Seleccionar imagenes", command=self._select_files).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ttk.Button(controls, text="Seleccionar carpeta", command=self._select_folder).grid(
            row=0, column=1, sticky="ew", padx=8
        )
        ttk.Button(controls, text="Carpeta de salida", command=self._select_output_dir).grid(
            row=0, column=2, sticky="ew", padx=(8, 0)
        )

        selected_frame = ttk.LabelFrame(root, text="Seleccion")
        selected_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        selected_frame.columnconfigure(0, weight=1)
        selected_frame.rowconfigure(0, weight=1)

        self.selected_list = tk.Listbox(selected_frame, height=8)
        self.selected_list.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        scrollbar = ttk.Scrollbar(selected_frame, orient=tk.VERTICAL, command=self.selected_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=8)
        self.selected_list.configure(yscrollcommand=scrollbar.set)

        options = ttk.LabelFrame(root, text="Opciones")
        options.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        options.columnconfigure(1, weight=1)

        ttk.Label(options, text="Anonimizacion").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        method_frame = ttk.Frame(options)
        method_frame.grid(row=0, column=1, sticky="w", padx=8, pady=8)
        ttk.Radiobutton(method_frame, text="Desenfoque", variable=self.method, value="desenfoque").pack(
            side=tk.LEFT, padx=(0, 12)
        )
        ttk.Radiobutton(method_frame, text="Pixelado", variable=self.method, value="pixelado").pack(
            side=tk.LEFT, padx=(0, 12)
        )
        ttk.Radiobutton(method_frame, text="Recuadro negro", variable=self.method, value="negro").pack(side=tk.LEFT)

        checks = ttk.Frame(options)
        checks.grid(row=1, column=1, sticky="w", padx=8, pady=(0, 8))
        ttk.Checkbutton(checks, text="Detectar caras", variable=self.detect_faces_enabled).pack(
            side=tk.LEFT, padx=(0, 18)
        )
        ttk.Checkbutton(checks, text="Detectar matriculas", variable=self.detect_plates_enabled).pack(
            side=tk.LEFT
        )

        ttk.Label(options, text="Salida").grid(row=2, column=0, sticky="w", padx=8, pady=(0, 8))
        ttk.Label(options, textvariable=self.output_dir).grid(row=2, column=1, sticky="ew", padx=8, pady=(0, 8))

        ttk.Label(options, text="Debug").grid(row=3, column=0, sticky="w", padx=8, pady=(0, 8))
        ttk.Checkbutton(
            options,
            text="Guardar imagenes anotadas con las detecciones dibujadas",
            variable=self.save_annotated_debug,
        ).grid(row=3, column=1, sticky="w", padx=8, pady=(0, 8))

        confidence_button = ttk.Checkbutton(
            options,
            text="Confianzas avanzadas v",
            variable=self.show_confidence_options,
            command=self._toggle_confidence_options,
            style="Toolbutton",
        )
        confidence_button.grid(row=4, column=0, sticky="w", padx=8, pady=(0, 8))

        self.confidence_frame = ttk.Frame(options)
        self.confidence_frame.columnconfigure(1, weight=1)
        self.confidence_frame.columnconfigure(2, minsize=48)
        self._add_confidence_slider(
            self.confidence_frame,
            row=0,
            label="Caras",
            variable=self.face_confidence,
            minimum=MIN_SLIDER_CONFIDENCE,
        )
        self._add_confidence_slider(
            self.confidence_frame,
            row=1,
            label="Matriculas directas",
            variable=self.plate_confidence,
            minimum=MIN_SLIDER_CONFIDENCE,
        )
        self._add_confidence_slider(
            self.confidence_frame,
            row=2,
            label="Matriculas con vehiculo",
            variable=self.plate_context_confidence,
            minimum=MIN_SLIDER_CONFIDENCE,
        )
        self._add_confidence_slider(
            self.confidence_frame,
            row=3,
            label="Vehiculos",
            variable=self.vehicle_confidence,
            minimum=MIN_SLIDER_CONFIDENCE,
        )
        ttk.Button(self.confidence_frame, text="Restablecer", command=self._reset_confidences).grid(
            row=4, column=1, sticky="e", padx=8, pady=(4, 8)
        )

        bottom = ttk.Frame(root)
        bottom.grid(row=4, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(bottom, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.process_button = ttk.Button(bottom, text="Procesar imagenes", command=self._start_processing)
        self.process_button.grid(row=0, column=1)

        ttk.Label(root, textvariable=self.status).grid(row=5, column=0, sticky="w", pady=(10, 0))

    def _select_files(self) -> None:
        filenames = filedialog.askopenfilenames(
            title="Selecciona imagenes",
            filetypes=[
                ("Imagenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if filenames:
            self._set_selected_paths([Path(name) for name in filenames])

    def _select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Selecciona una carpeta con imagenes")
        if folder:
            self._set_selected_paths([Path(folder)])

    def _select_output_dir(self) -> None:
        folder = filedialog.askdirectory(title="Selecciona la carpeta de salida")
        if folder:
            self.output_dir.set(folder)

    def _toggle_confidence_options(self) -> None:
        if self.show_confidence_options.get():
            self.confidence_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        else:
            self.confidence_frame.grid_remove()

    def _add_confidence_slider(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        variable: tk.DoubleVar,
        minimum: float,
    ) -> None:
        value_label = ttk.Label(parent, width=5)

        def update_value(_value: str | None = None) -> None:
            value_label.configure(text=f"{variable.get():.2f}")

        variable.trace_add("write", lambda *_args: update_value())

        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
        scale = ttk.Scale(
            parent,
            from_=minimum,
            to=1.0,
            variable=variable,
            command=update_value,
        )
        scale.grid(row=row, column=1, sticky="ew", padx=8, pady=4)
        value_label.grid(row=row, column=2, sticky="e", pady=4)
        update_value()

    def _reset_confidences(self) -> None:
        self.face_confidence.set(MIN_FACE_CONFIDENCE)
        self.plate_confidence.set(MIN_STANDALONE_PLATE_CONFIDENCE)
        self.plate_context_confidence.set(MIN_CONTEXT_PLATE_CONFIDENCE)
        self.vehicle_confidence.set(MIN_VEHICLE_CONFIDENCE)

    def _set_selected_paths(self, paths: list[Path]) -> None:
        self.selected_paths = paths
        default_output_dir = default_output_dir_for_paths(paths, self.project_root / "output")
        self.output_dir.set(str(default_output_dir))
        self.selected_list.delete(0, tk.END)
        for path in paths:
            self.selected_list.insert(tk.END, str(path))
        image_count = len(collect_images(paths))
        self.status.set(f"{image_count} imagen(es) listas para procesar.")

    def _start_processing(self) -> None:
        if not self.selected_paths:
            messagebox.showwarning("Faltan imagenes", "Selecciona una o varias imagenes, o una carpeta.")
            return
        if not self.detect_faces_enabled.get() and not self.detect_plates_enabled.get():
            messagebox.showwarning("Falta deteccion", "Activa caras, matriculas o ambas opciones.")
            return

        images = collect_images(self.selected_paths)
        if not images:
            messagebox.showwarning("Sin imagenes", "No se encontraron imagenes compatibles.")
            return

        try:
            required_models = []
            if self.detect_faces_enabled.get():
                required_models.append(self.face_model_path)
            if self.detect_plates_enabled.get():
                required_models.append(self.plate_model_path)
                required_models.append(self.vehicle_model_path)
            check_yolo_ready(required_models)
        except Exception as exc:
            messagebox.showerror("Faltan modelos YOLO", str(exc))
            return

        self.process_button.configure(state=tk.DISABLED)
        self.progress.set(0)
        self.status.set("Procesando imagenes...")
        save_annotated_debug = self.save_annotated_debug.get()
        thread = threading.Thread(target=self._process_images, args=(images, save_annotated_debug), daemon=True)
        thread.start()

    def _process_images(self, images: list[Path], save_annotated_debug: bool) -> None:
        result = ProcessResult()
        output_dir = Path(self.output_dir.get())
        annotated_dir = default_annotated_dir_for_paths(
            self.selected_paths,
            output_dir.parent / f"{output_dir.name}_anotadas",
        )
        total = len(images)

        for index, image_path in enumerate(images, start=1):
            try:
                image = read_image(image_path)
                if image is None:
                    raise ValueError("No se pudo abrir la imagen.")

                boxes = []
                face_boxes = []
                plate_boxes = []
                face_count = 0
                plate_count = 0
                if self.detect_faces_enabled.get():
                    face_boxes = detect_faces(image, self.face_model_path, self.face_confidence.get())
                    boxes.extend(face_boxes)
                    face_count = len(face_boxes)
                if self.detect_plates_enabled.get():
                    plate_boxes = detect_plates(
                        image,
                        self.plate_model_path,
                        self.plate_confidence.get(),
                        self.vehicle_model_path,
                        context_confidence=self.plate_context_confidence.get(),
                        vehicle_confidence=self.vehicle_confidence.get(),
                    )
                    boxes.extend(plate_boxes)
                    plate_count = len(plate_boxes)

                anonymized = anonymize_regions(image, boxes, self.method.get())
                output_path = make_output_path(image_path, output_dir)
                if not write_image(output_path, anonymized, source_path=image_path):
                    raise ValueError("No se pudo guardar la imagen procesada.")

                if save_annotated_debug:
                    annotated_image = draw_debug_detections(image, self._detect_debug_detections(image))
                    annotated_path = make_output_path(image_path, annotated_dir, suffix="_anotada")
                    if not write_image(annotated_path, annotated_image, source_path=image_path):
                        raise ValueError("No se pudo guardar la imagen anotada de depuracion.")

                result.processed += 1
                result.faces += face_count
                result.plates += plate_count
                logging.info(
                    "Procesada %s -> %s. Caras=%s Matriculas=%s",
                    image_path,
                    output_path,
                    face_count,
                    plate_count,
                )
            except Exception as exc:
                result.errors += 1
                logging.error("Error procesando %s: %s\n%s", image_path, exc, traceback.format_exc())

            progress = index * 100 / total
            self.after(0, self._update_progress, progress, index, total)

        self.after(0, self._finish_processing, result, output_dir, annotated_dir if save_annotated_debug else None)

    def _detect_debug_detections(self, image) -> list[tuple[str, Detection]]:
        detections: list[tuple[str, Detection]] = []

        if self.detect_faces_enabled.get():
            detections.extend(
                ("cara", detection)
                for detection in detect_with_yolo_details(
                    image,
                    self.face_model_path,
                    self.face_confidence.get(),
                    class_names=FACE_CLASS_NAMES,
                )
            )

        if self.detect_plates_enabled.get():
            plate_confidence = min(self.plate_confidence.get(), self.plate_context_confidence.get())
            detections.extend(
                ("matricula", detection)
                for detection in detect_with_yolo_details(
                    image,
                    self.plate_model_path,
                    plate_confidence,
                    class_names=PLATE_CLASS_NAMES,
                    image_size=PLATE_IMAGE_SIZE,
                )
            )
            detections.extend(
                ("vehiculo", detection)
                for detection in detect_with_yolo_details(
                    image,
                    self.vehicle_model_path,
                    self.vehicle_confidence.get(),
                    class_names=VEHICLE_CLASS_NAMES,
                    image_size=VEHICLE_IMAGE_SIZE,
                )
            )

        return detections

    def _update_progress(self, progress: float, index: int, total: int) -> None:
        self.progress.set(progress)
        self.status.set(f"Procesando {index} de {total} imagen(es)...")

    def _finish_processing(self, result: ProcessResult, output_dir: Path, annotated_dir: Path | None) -> None:
        self.process_button.configure(state=tk.NORMAL)
        self.status.set(
            f"Listo. Procesadas: {result.processed}. Errores: {result.errors}. Salida: {output_dir}"
        )
        annotated_summary = f"\nImagenes anotadas: {annotated_dir}" if annotated_dir else ""
        messagebox.showinfo(
            "Procesamiento completado",
            "Resumen:\n"
            f"Imagenes procesadas: {result.processed}\n"
            f"Errores: {result.errors}\n"
            f"Caras detectadas: {result.faces}\n"
            f"Matriculas detectadas: {result.plates}\n\n"
            f"Carpeta de salida: {output_dir}"
            f"{annotated_summary}\n\n"
            "Revisa las imagenes antes de compartirlas. La deteccion automatica puede no ser perfecta.",
        )
