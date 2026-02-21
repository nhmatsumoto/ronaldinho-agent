# Ronaldinho ConfigUI Launcher
# This script starts the modern governance interface for the agent.

$ConfigUIDir = Join-Path $PSScriptRoot "..\services\Ronaldinho.ConfigUI"

if (-not (Test-Path $ConfigUIDir)) {
    Write-Error "Could not find ConfigUI directory at $ConfigUIDir"
    exit 1
}

Write-Host "⚽ Launching Ronaldinho Governance Interface... 🚀" -ForegroundColor Cyan
Write-Host "[*] Directory: $ConfigUIDir" -ForegroundColor Gray

# Check for node_modules
if (-not (Test-Path (Join-Path $ConfigUIDir "node_modules"))) {
    Write-Host "[!] Missing dependencies. Running npm install..." -ForegroundColor Yellow
    Set-Location $ConfigUIDir
    npm install
}

Set-Location $ConfigUIDir

# Start the dev server
Write-Host "[*] Starting Vite Dev Server on http://localhost:5173" -ForegroundColor Green
npm run dev
