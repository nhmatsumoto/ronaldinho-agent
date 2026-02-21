# Ronaldinho Neural Core Startup
Write-Host "⚽ Starting Ronaldinho Neural Core (Hyper-Converged)..." -ForegroundColor Cyan

# Check for .NET
if (!(Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Error "❌ .NET SDK not found. Please install .NET 9."
    exit 1
}

$projectPath = "services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj"

if (!(Test-Path $projectPath)) {
    Write-Error "❌ Project file not found at $projectPath"
    exit 1
}

# Check for configuration
$envPath = ".env"
$isConfigured = $false

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    # Check if we have a Telegram token AND at least one LLM key that isn't a placeholder
    $hasTelegram = $envContent -match "TELEGRAM_BOT_TOKEN=[\w:-]{15,}"
    $hasLLM = ($envContent -match "GEMINI_API_KEY=AIza[\w-]{30,}") -or 
               ($envContent -match "OPENAI_API_KEY=sk-[\w-]{30,}") -or 
               ($envContent -match "ANTHROPIC_API_KEY=sk-ant-[\w-]{30,}")

    if ($hasTelegram -and $hasLLM) {
        $isConfigured = $true
    }
}

# Run the project
Write-Host "🧠 Orchestrating NeuralCore..." -ForegroundColor Green
$neuralCorePath = "services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj"
$bridgePath = "services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj"

# Always start NeuralCore (it provides the API for the UI)
Start-Process dotnet -ArgumentList "run --project `"$neuralCorePath`"" -WindowStyle Normal

if ($isConfigured) {
    Write-Host "✅ Configuration detected. Launching Telegram Bridge..." -ForegroundColor Cyan
    Start-Process dotnet -ArgumentList "run --project `"$bridgePath`"" -WindowStyle Normal
    Write-Host "⚽ Ronaldinho is ready and listening." -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Ronaldinho is UNCONFIGURED." -ForegroundColor Yellow
    Write-Host "🚀 Launching Governance Interface for initial setup..." -ForegroundColor Green
    
    # Launch ConfigUI
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `".\dev_scripts\start_ui.ps1`"" -WindowStyle Normal
    
    # Give it a moment and open browser
    Start-Sleep -Seconds 5
    Start-Process "http://localhost:5173"
    
    Write-Host "📌 Please complete the setup in your browser to start using Ronaldinho." -ForegroundColor Yellow
}
