@echo off
echo.
echo  ========================================
echo   SAHAF - Kurulum / Installation
echo  ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] Python bulunamadi. Lutfen Python 3.10+ yukleyin.
    echo      https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [1/2] Bagimliliklar yukleniyor...
pip install -e .
if errorlevel 1 (
    echo  [!] Kurulum basarisiz oldu.
    pause
    exit /b 1
)

echo.
echo  [2/2] Kurulum tamamlandi!
echo.
echo  Baslatmak icin: start.bat
echo.
pause
