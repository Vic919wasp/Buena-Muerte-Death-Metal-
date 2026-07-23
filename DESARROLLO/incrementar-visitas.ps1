# ============================================================
# CONTEXTO: Script para incrementar contador de visitas del sitio
#           Buena Muerte. Lee y escribe visits.json.
# ============================================================
# ÍNDICE DE NAVEGACIÓN
# [001] LECTURA/ESCRITURA    - línea 9
# ============================================================

$root = $PSScriptRoot
if (-not $root) { $root = Split-Path -Parent $MyInvocation.MyCommand.Path }
$jsonPath = Join-Path $root "visits.json"
$json = Get-Content $jsonPath -Raw | ConvertFrom-Json
$json.visits++
$json.updated = Get-Date -Format "yyyy-MM-dd"
$json | ConvertTo-Json | Set-Content $jsonPath -Encoding UTF8
Write-Host "Visitas: $($json.visits)"
