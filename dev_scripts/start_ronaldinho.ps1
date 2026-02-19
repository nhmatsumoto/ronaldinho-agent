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
python gemini_cli.py start
