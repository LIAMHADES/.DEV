# ============================================================
#  ARES/GPS — Restaurar archivos desde el ultimo snapshot bueno
#  Uso:  doble clic en restaurar.bat
#  Que hace: te muestra los snapshots guardados y restaura los
#  archivos al estado que elijas. Ideal cuando un cambio ha
#  vaciado o roto una pagina.
# ============================================================

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

Write-Host "=== ARES/GPS — Restaurar desde snapshot ===" -ForegroundColor Cyan
Write-Host "Proyecto: $repo`n"

# Mostrar archivos actualmente corruptos
Write-Host "Archivos corruptos AHORA MISMO (vacios / cero-relleno):" -ForegroundColor Yellow
$corruptos = @()
Get-ChildItem -Recurse -File -Include *.html,*.css,*.js,*.md,*.py,*.json,*.txt |
  Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -notmatch '\\\.backups\\' } |
  ForEach-Object {
    $bad = $false
    if ($_.Length -eq 0) { $bad = $true }
    else {
      $head = [System.IO.File]::ReadAllBytes($_.FullName) | Select-Object -First 512
      if (($head | Where-Object { $_ -ne 0 }).Count -eq 0) { $bad = $true }
    }
    if ($bad) { $corruptos += $_.FullName.Replace("$repo\","") }
  }
if ($corruptos.Count -gt 0) { $corruptos | ForEach-Object { Write-Host "   $_" -ForegroundColor Red } }
else { Write-Host "   (ninguno)" -ForegroundColor Green }

Write-Host "`nUltimos snapshots disponibles:" -ForegroundColor Yellow
git log --oneline -12 --pretty=format:"  %h  %ad  %s" --date=format:"%Y-%m-%d %H:%M"
Write-Host "`n"

Write-Host "OPCIONES:" -ForegroundColor Cyan
Write-Host "  [A] Restaurar SOLO un archivo concreto (recomendado)"
Write-Host "  [B] Restaurar TODO al ultimo snapshot (descarta cambios sin guardar)"
Write-Host "  [C] Cancelar"
$op = Read-Host "`nElige A / B / C"

switch ($op.ToUpper()) {
  "A" {
    $ruta = Read-Host "Ruta del archivo a restaurar (ej: landing/contenido/descanso.html)"
    $commit = Read-Host "Hash del snapshot (deja vacio para el ultimo)"
    if ([string]::IsNullOrWhiteSpace($commit)) { $commit = "HEAD" }
    git checkout $commit -- "$ruta"
    Write-Host "`n  Restaurado '$ruta' desde $commit." -ForegroundColor Green
  }
  "B" {
    Write-Host "`n  ATENCION: esto descarta TODOS los cambios no guardados." -ForegroundColor Red
    $conf = Read-Host "  Escribe SI para confirmar"
    if ($conf -eq "SI") {
      git checkout -- .
      Write-Host "`n  Todo restaurado al ultimo snapshot." -ForegroundColor Green
    } else { Write-Host "  Cancelado." -ForegroundColor Gray }
  }
  default { Write-Host "  Cancelado." -ForegroundColor Gray }
}
Read-Host "`nPulsa ENTER para cerrar"
