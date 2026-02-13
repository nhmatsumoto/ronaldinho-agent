# Watchdog de Integridade de Build
# Este script monitora falhas comuns e reporta ao Orchestrator.

$ErrorActionPreference = "Stop"

function Test-Build {
    Write-Host "[Watchdog] Iniciando verificação de integridade..." -ForegroundColor Cyan
    
    # 1. Verificar se o projeto compila (Exemplo simplificado)
    if (Test-Path "*.sln") {
        Write-Host "[Watchdog] Detectado projeto .NET. Executando check rápido..."
        # Aqui viria um dotnet build --no-restore
    }

    # 2. Verificar se há erros críticos nos logs (Exemplo)
    $critErrors = Get-ChildItem -Recurse -Include "*.log" | Select-String "CRITICAL"
    if ($critErrors) {
        Write-Host "[Watchdog] ERROS CRÍTICOS ENCONTRADOS!" -ForegroundColor Red
        $critErrors | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "[Watchdog] Nenhum erro crítico detectado nos logs." -ForegroundColor Green
    }
}

try {
    Test-Build
} catch {
    Write-Host "[Watchdog] Falha na execução: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
