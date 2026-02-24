#!/bin/bash

# Ronaldinho Agent: Killer Script 🏀💀
# This script identifies and kills all processes related to the Ronaldinho ecosystem.

echo -e "\e[31m[*] Desligando Ronaldinho Agent...\e[0m"

# 1. Kill by Ports (Dashboard and Core)
echo "[*] Limpando portas 3000 (Dashboard) e 5000 (Neural Core)..."
fuser -k 3000/tcp 5000/tcp > /dev/null 2>&1

# 2. Kill by Process Names (Bridge and Signaling)
echo "[*] Parando processos Python (Bridge, Signaling)..."
pkill -f "src/bridge/main.py"
pkill -f "signaling_server.py"

# 3. Kill Monitor (if running)
echo "[*] Parando Monitor de Evolução..."
pkill -f "monitor_evolution.sh"

echo -e "\e[32m[!] Ronaldinho está fora de campo. Até a próxima! 🏟️\e[0m"
