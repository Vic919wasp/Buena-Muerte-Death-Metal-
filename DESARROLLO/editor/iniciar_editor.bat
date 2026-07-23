@echo off
echo ========================================
echo  Buena Muerte — Editor de Contenido
echo ========================================
cd /d "%~dp0"
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
echo Iniciando editor...
python main.py
pause
