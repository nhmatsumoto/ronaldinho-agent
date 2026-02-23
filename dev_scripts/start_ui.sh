#!/bin/bash
# Ronaldinho ConfigUI Launcher (Linux/macOS)
# This script starts the modern governance interface for the agent.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_UI_DIR="$SCRIPT_DIR/../services/Ronaldinho.ConfigUI"

if [ ! -d "$CONFIG_UI_DIR" ]; then
    echo "❌ Could not find ConfigUI directory at $CONFIG_UI_DIR"
    exit 1
fi

echo "⚽ Launching Ronaldinho Governance Interface... 🚀"
echo "[*] Directory: $CONFIG_UI_DIR"

# Check for node_modules
if [ ! -d "$CONFIG_UI_DIR/node_modules" ]; then
    echo "[!] Missing dependencies. Running npm install..."
    cd "$CONFIG_UI_DIR" || exit 1
    npm install
fi

cd "$CONFIG_UI_DIR" || exit 1

# Start the dev server
echo "[*] Starting Vite Dev Server on http://localhost:5173"
npm run dev
