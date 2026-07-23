# export-newsletter.ps1
# Exporta emails suscritos del newsletter a un archivo JSON
# Uso: .\export-newsletter.ps1
# O importar desde localStorage manualmente via admin.html

$jsonPath = "newsletter.json"

if (-not (Test-Path $jsonPath)) {
    Write-Host "Creando newsletter.json vacio..." -ForegroundColor Yellow
    @{ subscribers = @() } | ConvertTo-Json | Set-Content $jsonPath -Encoding UTF8
}

$data = Get-Content $jsonPath -Raw | ConvertFrom-Json
$subs = $data.subscribers

Write-Host "`n=== Newsletter Subscribers ===" -ForegroundColor Cyan
Write-Host "Total: $($subs.Count) emails`n" -ForegroundColor Green

if ($subs.Count -eq 0) {
    Write-Host "No hay suscriptos aun." -ForegroundColor Yellow
} else {
    $subs | ForEach-Object {
        Write-Host "  $($_.email)  ($($_.date))" -ForegroundColor White
    }
    
    # Exportar a CSV para usar en servicios de email
    $csvPath = "newsletter-subscribers.csv"
    $subs | Select-Object email, date | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
    Write-Host "`nExportado a $csvPath" -ForegroundColor Green
}

Write-Host "`nPara agregar emails manualmente, edita newsletter.json" -ForegroundColor Gray
Write-Host "O usa admin.html en el navegador para gestionar suscriptos.`n" -ForegroundColor Gray
