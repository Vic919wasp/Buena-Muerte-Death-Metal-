@echo off
echo ========================================
echo  Buena Muerte — Editor de Contenido
echo ========================================
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (
    echo Creando entorno virtual...
    python -m venv venv
)
echo Instalando dependencias...
"venv\Scripts\python.exe" -m pip install -r requirements.txt
echo Iniciando editor...
set QT_LOGGING_RULES=*.warning=false
set QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu --in-process-gpu --disable-software-rasterizer --disk-cache-size=0 --media-cache-size=0 --aggressive-cache-discard
"venv\Scripts\python.exe" main.py
pause
