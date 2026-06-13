@echo off
setlocal
cd /d "%~dp0\.."

if not exist ".venv\Scripts\activate.bat" (
    echo Falta la instalacion inicial.
    echo Ejecuta primero install_windows.bat haciendo doble clic.
    echo.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
python "models\download_models.py"
if errorlevel 1 (
    echo.
    echo No se pudieron descargar los modelos.
    echo Revisa tu conexion a internet o descarga los archivos manualmente en la carpeta models.
    echo.
    pause
    exit /b 1
)

echo.
pause
