@echo off
echo.
echo  ========================================
echo   SAHAF - PDF / EPUB to Markdown
echo  ========================================
echo.
echo  Sunucu baslatiliyor...
echo  Tarayicida ac: http://localhost:8000
echo.
echo  Durdurmak icin: Ctrl+C
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
