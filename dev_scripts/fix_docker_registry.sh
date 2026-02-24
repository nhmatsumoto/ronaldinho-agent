#!/bin/bash

# Ronaldinho Docker Registry Rescue
# This script helps diagnose and fix "401 Unauthorized" or "429" errors from mcr.microsoft.com

echo -e "\e[36m🛡️ Ronaldinho Docker Registry Rescue...\e[0m"

echo -e "\n\e[33m[*] Esclarecimento Importante:\e[0m"
echo "O erro '401 Unauthorized' ou '429' que você está vendo no Docker NÃO é uma falha de login"
echo "do Ronaldinho ou falta de chaves de API. É um bloqueio do Registry da Microsoft (MCR)."
echo "Isso acontece quando há muitas requisições anônimas ou instabilidade no servidor da MS."

echo -e "\n\e[90m[*] Tentando diagnosticar conexão com mcr.microsoft.com...\e[0m"
if curl -I "https://mcr.microsoft.com/v2/" > /dev/null 2>&1; then
    echo -e "\e[32m✅ Conexão básica com o MCR estabelecida.\e[0m"
else
    echo -e "\e[31m❌ Falha ao conectar ao MCR.\e[0m"
fi

echo -e "\n\e[36m[*] Sugestões de Correção:\e[0m"
echo "1. Rode 'docker logout mcr.microsoft.com' para limpar tokens anônimos expirados."
echo "2. Tente baixar a imagem manualmente fora do Compose: 'docker pull mcr.microsoft.com/dotnet/sdk:9.0'"
echo "3. Verifique se o relógio do sistema está sincronizado (essencial para handshake HTTPS)."
echo "4. Use o Ronaldinho NATIVO (sem Docker) enquanto o MCR não estabiliza: './start_ronaldinho.sh'"

echo -e "\n\e[32m🚀 O Ronaldinho NATIVO já está funcionando no seu PC e não depende desses downloads agora.\e[0m"
