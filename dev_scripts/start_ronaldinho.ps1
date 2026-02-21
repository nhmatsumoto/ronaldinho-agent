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

Write-Host "🧠 Orchestrating Bridge and Brain..." -ForegroundColor Green

# Use absolute paths relative to root
$rootPath = Resolve-Path ".."
$neuralCorePath = "$rootPath/services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj"
$bridgePath = "$rootPath/services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj"

# Start services in separate windows/jobs to allow parallel execution
Write-Host "🚀 Launching NeuralCore..." -ForegroundColor Yellow
Start-Process dotnet -ArgumentList "run --project `"$neuralCorePath`"" -WindowStyle Normal

Write-Host "🚀 Launching Telegram Bridge..." -ForegroundColor Yellow
Start-Process dotnet -ArgumentList "run --project `"$bridgePath`"" -WindowStyle Normal

Write-Host "✅ Systems online. Ronaldinho is ready." -ForegroundColor Cyan
