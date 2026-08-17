# ============================================================
#  ARES/GPS — Snapshot de seguridad (git local)
#  Uso:  doble clic en snapshot.bat  (o ejecutar este .ps1)
#  Que hace: guarda una "foto" del estado actual de TODO el
#  proyecto en el historial git local. Si un cambio corrompe
#  o vacia un archivo, puedes volver a esta foto al instante.
# ============================================================

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot   # carpeta padre de Scripts/ = raiz del proyecto
Set-Location $repo

Write-Host "=== ARES/GPS — Snapshot de seguridad ===" -ForegroundColor Cyan
Write-Host "Proyecto: $repo`n"

# 1. Detectar archivos corruptos (0 bytes o cero-relleno) ANTES de guardar
Write-Host "[1/3] Comprobando integridad de archivos de texto..." -ForegroundColor Yellow
$corruptos = @()
Get-ChildItem -Recurse -File -Include *.html,*.css,*.js,*.md,*.py,*.json,*.txt |
  Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -notmatch '\\\.backups\\' } |
  ForEach-Object {
    if ($_.Length -eq 0) {
      $corruptos += "VACIO (0 bytes): $($_.FullName)"
    } else {
      $head = [System.IO.File]::ReadAllBytes($_.FullName) | Select-Object -First 512
      $nonZero = ($head | Where-Object { $_ -ne 0 }).Count
      if ($nonZero -eq 0) { $corruptos += "CERO-RELLENO: $($_.FullName)" }
    }
  }

if ($corruptos.Count -gt 0) {
  Write-Host "`n  AVISO: hay archivos posiblemente corruptos:" -ForegroundColor Red
  $corruptos | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
  Write-Host "  Recupera esos archivos con:  Scripts\restaurar.bat`n" -ForegroundColor Red
} else {
  Write-Host "  OK — ningun archivo vacio ni cero-relleno.`n" -ForegroundColor Green
}

# 2. Guardar snapshot
Write-Host "[2/3] Guardando snapshot en git local..." -ForegroundColor Yellow
git add -A 2>&1 | Out-Null
$hayCambios = (git status --porcelain)
if ([string]::IsNullOrWhiteSpace($hayCambios)) {
  Write-Host "  Sin cambios desde el ultimo snapshot. Nada que guardar.`n" -ForegroundColor Gray
} else {
  $fecha = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  git commit -q -m "snapshot: $fecha"
  Write-Host "  Snapshot guardado: $fecha`n" -ForegroundColor Green
}

# 3. Resumen historial
Write-Host "[3/3] Ultimos snapshots guardados:" -ForegroundColor Yellow
git log --oneline -8 --date=short --pretty=format:"  %ad  %s" --date=format:"%Y-%m-%d %H:%M"
Write-Host "`n"
Write-Host "Listo. Ya puedes trabajar tranquilo." -ForegroundColor Cyan
Write-Host "Si algo se rompe, ejecuta:  Scripts\restaurar.bat" -ForegroundColor Cyan
Read-Host "`nPulsa ENTER para cerrar"
