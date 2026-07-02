#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

ask_yes_no() {
    local prompt="$1"
    local answer
    read -r -p "$prompt (S/N): " answer
    case "$answer" in
        S|s|SI|Si|si|Y|y|YES|Yes|yes) return 0 ;;
        *) return 1 ;;
    esac
}

echo "Desinstalando herramienta de anonimizacion..."
echo
echo "Este script elimina las dependencias instaladas dentro de esta carpeta."
echo "No borra Python ni modifica otras aplicaciones del equipo."
echo

if [ -d ".venv" ]; then
    echo "Eliminando entorno virtual local .venv..."
    rm -rf ".venv"
    echo "Entorno virtual eliminado."
else
    echo "No existe .venv. No hay dependencias locales que eliminar."
fi

echo
if ask_yes_no "Quieres borrar tambien los modelos descargados en models?"; then
    rm -f "models/yolo_faces.pt"
    rm -f "models/yolo_plates.pt"
    rm -f "models/yolov8n.pt"
    rm -f "models/MODELS_DOWNLOADED.md"
    echo "Modelos descargados eliminados."
fi

echo
if ask_yes_no "Quieres borrar logs y cache local de Ultralytics?"; then
    rm -rf "logs"
    echo "Logs eliminados."
fi

echo
if ask_yes_no "Quieres borrar la carpeta output de esta herramienta?"; then
    rm -rf "output"
    rm -rf "output_ubuntu_test"
    echo "Carpetas de salida locales eliminadas."
fi

echo
echo "Desinstalacion completada."
echo "Puedes borrar manualmente esta carpeta del proyecto si ya no la necesitas."
echo "Las carpetas de salida creadas junto a tus fotos no se borran automaticamente."
