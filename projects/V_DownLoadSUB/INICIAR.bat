@echo off
title V_DOWNLOADER — Iniciando...
cd /d "C:\Users\solde\OneDrive\Desktop\EJECUTER_EXT\V_DOWNLOADER"

echo.
echo   ========================================
echo     V_DOWNLOADER v9 — Video Downloader
echo   ========================================
echo.

:: Kill any existing server on port 5555
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5555.*LISTENING" 2^>nul') do (
    echo   Deteniendo servidor anterior...
    taskkill /F /PID %%a >nul 2>nul
)

:: Start the server in background
echo   Iniciando servidor...
start /min "" "venv\Scripts\python.exe" "app.py"

:: Wait for the server to be ready
echo   Esperando servidor...
:wait
timeout /t 1 /nobreak >nul
netstat -an 2>nul | findstr ":5555 " | findstr "LISTENING" >nul
if errorlevel 1 goto wait

:: Open the page
echo   Abriendo http://localhost:5555
start "" http://localhost:5555

echo   Listo.
exit
