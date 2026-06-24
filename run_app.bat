@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo No se encontro una instalacion previa.
    echo Se iniciara la instalacion automaticamente.
    echo.
    call "installer_scripts\install_windows.bat" --no-pause
    if errorlevel 1 (
        echo.
        echo No se pudo completar la instalacion.
        echo Revisa los mensajes anteriores.
        echo.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"
python -m src.main
if errorlevel 1 (
    echo.
    echo La aplicacion se cerro con un error.
    echo Revisa la carpeta logs o vuelve a ejecutar installer_scripts\install_windows.bat.
    echo.
    pause
    exit /b 1
)
