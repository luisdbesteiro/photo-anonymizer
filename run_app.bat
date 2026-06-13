@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Falta la instalacion inicial.
    echo Ejecuta primero install_windows.bat haciendo doble clic.
    echo.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m src.main
if errorlevel 1 (
    echo.
    echo La aplicacion se cerro con un error.
    echo Revisa la carpeta logs o vuelve a ejecutar install_windows.bat.
    echo.
    pause
    exit /b 1
)
