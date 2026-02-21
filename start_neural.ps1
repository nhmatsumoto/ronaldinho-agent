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

# Run the project
Write-Host "🧠 Orchestrating NeuralCore and Bridge..." -ForegroundColor Green
$neuralCorePath = "services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj"
$bridgePath = "services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj"

Start-Process dotnet -ArgumentList "run --project `"$neuralCorePath`"" -WindowStyle Normal
Start-Process dotnet -ArgumentList "run --project `"$bridgePath`"" -WindowStyle Normal

Write-Host "✅ Ronaldinho is ready (Hyper-Converged)." -ForegroundColor Cyan
