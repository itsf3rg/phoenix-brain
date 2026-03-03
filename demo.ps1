$ErrorActionPreference = "Stop"

$port = 8000
$tcpConnections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($tcpConnections) {
    Write-Host "Port $port is in use. Stopping conflicting processes..."
    $tcpConnections | ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Stopping Process $($process.Name) (ID: $($process.Id))"
            Stop-Process -Id $process.Id -Force
        }
    }
    Start-Sleep -Seconds 2
}

$venvPath = Join-Path $PSScriptRoot "backend\venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Starting FastAPI Backend..."
$backendProcess = Start-Process -PassThru -NoNewWindow -FilePath $pythonExe -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8000" -WorkingDirectory (Join-Path $PSScriptRoot "backend")
Start-Sleep -Seconds 3

Write-Host "Opening Command Center Web Dashboard..."
$dashboardHtml = Join-Path $PSScriptRoot "dashboard\index.html"
Start-Process $dashboardHtml
Start-Sleep -Seconds 2

Write-Host "Injecting Mock Uber & Lyft Payloads..."
& $pythonExe test_offer.py

Write-Host "Local testing demo complete!"
