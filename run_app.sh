#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -f ".venv/bin/activate" ]; then
    echo "No se encontro una instalacion previa."
    echo "Se iniciara la instalacion automaticamente."
    echo
    if ! bash "installer_scripts/install_linux.sh" --no-pause; then
        echo
        echo "No se pudo completar la instalacion."
        echo "Revisa los mensajes anteriores."
        exit 1
    fi
fi

. ".venv/bin/activate"

if ! python -m src.main; then
    echo
    echo "La aplicacion se cerro con un error."
    echo "Revisa la carpeta logs o vuelve a ejecutar installer_scripts/install_linux.sh."
    exit 1
fi
