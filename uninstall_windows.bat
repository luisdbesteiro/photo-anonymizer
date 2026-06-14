@echo off
setlocal
cd /d "%~dp0"

echo Desinstalando herramienta de anonimizacion...
echo.
echo Este script elimina las dependencias instaladas dentro de esta carpeta.
echo No borra Python ni modifica otras aplicaciones del equipo.
echo.

if exist ".venv" (
    echo Eliminando entorno virtual local .venv...
    rmdir /s /q ".venv"
    if errorlevel 1 (
        echo No se pudo eliminar .venv.
        echo Cierra cualquier ventana de la aplicacion o terminal que la este usando y vuelve a intentarlo.
        echo.
        pause
        exit /b 1
    )
    echo Entorno virtual eliminado.
) else (
    echo No existe .venv. No hay dependencias locales que eliminar.
)

echo.
choice /c SN /n /m "Quieres borrar tambien los modelos descargados en models? (S/N): "
if errorlevel 2 goto skip_models
if exist "models\yolo_faces.pt" del /q "models\yolo_faces.pt"
if exist "models\yolo_plates.pt" del /q "models\yolo_plates.pt"
if exist "models\yolov8n.pt" del /q "models\yolov8n.pt"
if exist "models\MODELS_DOWNLOADED.md" del /q "models\MODELS_DOWNLOADED.md"
echo Modelos descargados eliminados.
:skip_models

echo.
choice /c SN /n /m "Quieres borrar logs y cache local de Ultralytics? (S/N): "
if errorlevel 2 goto skip_logs
if exist "logs" rmdir /s /q "logs"
echo Logs eliminados.
:skip_logs

echo.
choice /c SN /n /m "Quieres borrar la carpeta output de esta herramienta? (S/N): "
if errorlevel 2 goto skip_output
if exist "output" rmdir /s /q "output"
if exist "output_ubuntu_test" rmdir /s /q "output_ubuntu_test"
echo Carpetas de salida locales eliminadas.
:skip_output

echo.
echo Desinstalacion completada.
echo Puedes borrar manualmente esta carpeta del proyecto si ya no la necesitas.
echo Las carpetas de salida creadas junto a tus fotos no se borran automaticamente.
echo.
pause
