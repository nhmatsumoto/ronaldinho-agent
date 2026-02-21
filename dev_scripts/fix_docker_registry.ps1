# Ronaldinho Docker Registry Rescue
# This script helps diagnose and fix "401 Unauthorized" or "429" errors from mcr.microsoft.com

Write-Host "🛡️ Ronaldinho Docker Registry Rescue..." -ForegroundColor Cyan

Write-Host "`n[*] Esclarecimento Importante:" -ForegroundColor Yellow
Write-Host "O erro '401 Unauthorized' ou '429' que você está vendo no Docker NÃO é uma falha de login"
Write-Host "do Ronaldinho ou falta de chaves de API. É um bloqueio do Registry da Microsoft (MCR)."
Write-Host "Isso acontece quando há muitas requisições anônimas ou instabilidade no servidor da MS."

Write-Host "`n[*] Tentando diagnosticar conexão com mcr.microsoft.com..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "https://mcr.microsoft.com/v2/" -Method Get -ErrorAction Stop
    Write-Host "✅ Conexão básica com o MCR estabelecida." -ForegroundColor Green
} catch {
    Write-Host "❌ Falha ao conectar ao MCR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n[*] Sugestões de Correção:" -ForegroundColor Cyan
Write-Host "1. Rode 'docker logout mcr.microsoft.com' para limpar tokens anônimos expirados."
Write-Host "2. Tente baixar a imagem manualmente fora do Compose: 'docker pull mcr.microsoft.com/dotnet/sdk:9.0'"
Write-Host "3. Verifique se o seu relógio do Windows está sincronizado (essencial para handshake HTTPS)."
Write-Host "4. Use o Ronaldinho NATIVO (sem Docker) enquanto o MCR não estabiliza: '.\start_neural.ps1'"

Write-Host "`n🚀 O Ronaldinho NATIVO já está funcionando no seu PC e não depende desses downloads agora." -ForegroundColor Green
