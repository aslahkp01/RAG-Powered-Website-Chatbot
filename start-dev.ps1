$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"
$frontendDir = Join-Path $projectRoot "frontend"

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe. Create/activate your virtual environment first."
}

if (-not (Test-Path $frontendDir)) {
    throw "Frontend directory not found at $frontendDir."
}

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    Push-Location $frontendDir
    npm install
    Pop-Location
}

Write-Host "Starting FastAPI backend on http://127.0.0.1:8000 ..."
Start-Process powershell -WorkingDirectory $projectRoot -ArgumentList @(
    "-NoExit",
    "-Command",
    "& `"$pythonExe`" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
)

Write-Host "Starting React frontend (Vite) on http://127.0.0.1:5173 ..."
Start-Process powershell -WorkingDirectory $frontendDir -ArgumentList @(
    "-NoExit",
    "-Command",
    "npm run dev"
)

Write-Host "Done. Two new terminals were opened for backend and frontend."
