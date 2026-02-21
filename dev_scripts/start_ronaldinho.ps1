# Ronaldinho Startup Script
Write-Host "🚀 Initializing Ronaldinho System..." -ForegroundColor Cyan

# Check for .NET
if (!(Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Error "❌ .NET SDK not found. Please install .NET 9."
    exit 1
}

# Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "❌ Python not found. Please install Python 3."
    exit 1
}

# Check for configuration
$envPath = Join-Path $rootPath ".env"
$isConfigured = $false

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    $hasTelegram = $envContent -match "TELEGRAM_BOT_TOKEN=[\w:-]{15,}"
    $hasLLM = ($envContent -match "GEMINI_API_KEY=AIza[\w-]{30,}") -or 
               ($envContent -match "OPENAI_API_KEY=sk-[\w-]{30,}") -or 
               ($envContent -match "ANTHROPIC_API_KEY=sk-ant-[\w-]{30,}")

    if ($hasTelegram -and $hasLLM) {
        $isConfigured = $true
    }
}

Write-Host "🧠 Orchestrating NeuralCore..." -ForegroundColor Green

# 1. Start NeuralCore (API Provider)
Write-Host "🚀 Launching NeuralCore..." -ForegroundColor Yellow
Start-Process dotnet -ArgumentList "run --project `"$neuralCorePath`"" -WindowStyle Normal

if ($isConfigured) {
    Write-Host "🚀 Configuration valid. Launching Telegram Bridge..." -ForegroundColor Yellow
    Start-Process dotnet -ArgumentList "run --project `"$bridgePath`"" -WindowStyle Normal
    Write-Host "✅ Systems online. Ronaldinho is ready." -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Ronaldinho is UNCONFIGURED." -ForegroundColor Yellow
    Write-Host "🚀 Launching Governance Interface for initial setup..." -ForegroundColor Green
    
    $startUIScript = Join-Path $PSScriptRoot "start_ui.ps1"
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$startUIScript`"" -WindowStyle Normal
    
    Start-Sleep -Seconds 5
    Start-Process "http://localhost:5173"
    
    Write-Host "📌 Please complete the setup in your browser to activate the agent." -ForegroundColor Yellow
}
