#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -f ".venv/bin/activate" ]; then
    echo "Falta la instalacion inicial."
    echo "Crea el entorno e instala dependencias antes de ejecutar la aplicacion:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  python3 -m pip install -r requirements.txt"
    exit 1
fi

. ".venv/bin/activate"
python3 -m src.main
