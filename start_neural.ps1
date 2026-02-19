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
dotnet run --project $projectPath
