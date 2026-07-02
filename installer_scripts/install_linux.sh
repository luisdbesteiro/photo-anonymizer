#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
NO_PAUSE="${1:-}"

pause_if_needed() {
    if [ "$NO_PAUSE" != "--no-pause" ]; then
        printf "Pulsa Enter para continuar..."
        read -r _
    fi
}

echo "Instalando herramienta de anonimizacion..."
echo
echo "Comprobando Python..."

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "No se encontro Python."
    echo "Instala Python 3 con el gestor de paquetes de tu distribucion."
    echo "En Ubuntu/Debian suele ser: sudo apt install python3 python3-venv python3-tk"
    echo
    pause_if_needed
    exit 1
fi

echo "Creando entorno virtual..."
if ! "$PYTHON_CMD" -m venv .venv; then
    echo "No se pudo crear el entorno virtual."
    echo "Revisa que Python y el paquete venv esten instalados."
    echo "En Ubuntu/Debian suele ser: sudo apt install python3-venv"
    echo
    pause_if_needed
    exit 1
fi

echo "Instalando dependencias..."
. ".venv/bin/activate"
python -m pip install --upgrade pip
if ! python -m pip install -r "installer_scripts/requirements.txt"; then
    echo "No se pudieron instalar las dependencias."
    echo "Revisa tu conexion a internet y que Python este instalado correctamente."
    echo
    pause_if_needed
    exit 1
fi

echo "Descargando modelos YOLO..."
if ! python "src/download_models.py" --models-dir "models"; then
    echo "No se pudieron descargar todos los modelos necesarios."
    echo "Revisa tu conexion a internet o ejecuta installer_scripts/download_models_linux.sh mas tarde."
    echo
    pause_if_needed
    exit 1
fi

echo
echo "Instalacion completada."
echo "Puedes ejecutar la aplicacion usando ./run_app.sh"
echo
pause_if_needed
