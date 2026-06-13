@echo off
setlocal
cd /d "%~dp0"

echo Instalando herramienta de anonimizacion...
echo.
echo Comprobando Python...
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo No se encontro Python.
        echo Instala Python 3 desde https://www.python.org/downloads/ y marca la opcion "Add python.exe to PATH".
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
) else (
    set "PYTHON_CMD=py"
)

echo Creando entorno virtual...
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo No se pudo crear el entorno virtual.
    echo Revisa que Python este instalado correctamente.
    echo.
    pause
    exit /b 1
)

echo Instalando dependencias...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo No se pudieron instalar las dependencias.
    echo Revisa tu conexion a internet y que Python este instalado correctamente.
    echo.
    pause
    exit /b 1
)

echo.
echo Instalacion completada.
echo Puedes ejecutar la aplicacion usando run_app.bat
echo.
pause
