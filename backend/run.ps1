$venvPath = Join-Path $PSScriptRoot "venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Starting FastAPI backend..."
& $pythonExe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
