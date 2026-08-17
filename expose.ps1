# Script to expose ARES API to the internet using Pinggy.io
# This allows the mobile app to reach http://localhost:8000

Write-Host "🚀 Iniciando túnel para ARES API..." -ForegroundColor Cyan
Write-Host "⚠️  Copia la URL '.pinggy.link' que aparecerá abajo y ponla en tu App Android." -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para detener el túnel." -ForegroundColor Red

ssh -R 80:localhost:8000 ares-test@a.pinggy.io
