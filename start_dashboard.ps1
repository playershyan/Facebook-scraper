# PowerShell script to start dashboard server

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Dashboard Server" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

Write-Host "Starting dashboard server on http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Keep this window open to run the dashboard!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start dashboard server
python dashboard_server.py

