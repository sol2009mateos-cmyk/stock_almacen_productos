@echo off
chcp 65001 >nul
title StockMaster Pro v3.0
color 0A

echo ============================================
echo    STOCKMASTER PRO v3.0
echo ============================================
echo.

cd /d C:\Users\user\Documents\proyectos\stock_tienda

if errorlevel 1 (
    echo ERROR: No se pudo acceder a la carpeta.
    pause
    exit /b 1
)

echo Carpeta: %CD%
echo.

if not exist "venv\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR creando venv.
        pause
        exit /b 1
    )
    echo venv creado.
    echo.
)

echo Activando entorno...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR activando venv.
    pause
    exit /b 1
)
echo venv activado.
echo.

echo Verificando dependencias...
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo Instalando Pillow...
    pip install Pillow
    echo Pillow instalado.
) else (
    echo Pillow OK.
)
echo.

if not exist "productos_1000.json" (
    echo FALTA: productos_1000.json
    pause
    exit /b 1
)
if not exist "imagenes_productos" (
    echo FALTA: carpeta imagenes_productos
    pause
    exit /b 1
)
if not exist "app_inventario.py" (
    echo FALTA: app_inventario.py
    pause
    exit /b 1
)

echo Todo listo. Iniciando StockMaster Pro...
echo.
echo ============================================
echo    ABRIENDO SISTEMA...
echo ============================================
echo.

python app_inventario.py

echo.
echo ============================================
echo    Sistema cerrado.
echo ============================================
echo.

deactivate
pause
