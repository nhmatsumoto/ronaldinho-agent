#!/bin/bash

# Ronaldinho Agent: Unified Launcher (Python Edition)

echo "🏀 Ronaldinho Agent is starting (Reorganized Python Mode)..."

# 1. Start Signaling Server
python3 signaling_server.py &
SIGNALING_PID=$!

# 2. Start Neural Core (Python)
echo "[*] Starting Neural Core..."
cd services/core
python3 -m app.main &
NEURAL_PID=$!
cd ../..

# 3. Start Telegram Bridge (Python)
echo "[*] Starting Telegram Bridge..."
cd services/bridge
python3 bridge.py &
BRIDGE_PID=$!
cd ../..

# 4. Start Config UI (Frontend)
if [ -d "services/ui" ]; then
    echo "[*] Starting Config UI..."
    cd services/ui
    npm run dev -- --port 3000 &
    UI_PID=$!
    cd ../..
fi

echo "🚀 Ronaldinho is ready! Enjoy the fenomenal experience."
echo "Press Ctrl+C to stop all services."

trap "kill $SIGNALING_PID $NEURAL_PID $BRIDGE_PID $UI_PID; exit" INT
wait
