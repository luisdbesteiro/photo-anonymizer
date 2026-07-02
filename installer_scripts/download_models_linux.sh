#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

if [ ! -f ".venv/bin/activate" ]; then
    echo "Falta la instalacion inicial."
    echo "Ejecuta primero installer_scripts/install_linux.sh."
    exit 1
fi

. ".venv/bin/activate"

if ! python "src/download_models.py" --models-dir "models"; then
    echo
    echo "No se pudieron descargar los modelos."
    echo "Revisa tu conexion a internet o descarga los archivos manualmente en la carpeta models."
    exit 1
fi

echo
echo "Descarga de modelos completada."
