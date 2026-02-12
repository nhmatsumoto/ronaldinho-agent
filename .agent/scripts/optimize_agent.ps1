# optimize_agent.ps1
# internal script for agent self-diagnostics and optimization

function Get-ProjectStats {
    $RepoRoot = Resolve-Path "$PSScriptRoot\..\.."
    $CSharpFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter "*.cs" | Measure-Object | Select-Object -ExpandProperty Count
    $TsFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter "*.ts*" | Measure-Object | Select-Object -ExpandProperty Count
    
    Write-Host "Project Stats:"
    Write-Host "  C# Files: $CSharpFiles"
    Write-Host "  TypeScript/TSX Files: $TsFiles"
}

Write-Host "Running Agent Optimization Diagnostics..."
Get-ProjectStats
Write-Host "Optimization Complete."
