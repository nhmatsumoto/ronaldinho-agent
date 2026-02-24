#!/bin/bash

# Ronaldinho Agent: Unified Launcher (Background Edition)

echo "🏀 Ronaldinho Agent is starting (Pure Background Mode)..."

# Pre-flight: Kill any existing processes on ports 3000 and 5000
echo "[*] Cleaning up old processes..."
fuser -k 3000/tcp 5000/tcp > /dev/null 2>&1

# 0. Check Virtual Environment and Logs
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r services/core/requirements.txt"
    exit 1
fi

LOG_DIR="logs_v1"
mkdir -p $LOG_DIR
chmod +x start_ronaldinho.sh

PYTHON_BIN=$(pwd)/venv/bin/python3

# 1. Start Signaling Server
echo "[*] Starting Signaling Server..."
$PYTHON_BIN signaling_server.py > $LOG_DIR/signaling.log 2>&1 &
SIGNALING_PID=$!

# 2. Start Neural Core (Python)
echo "[*] Starting Neural Core..."
cd services/core
$PYTHON_BIN -m app.main > ../../$LOG_DIR/core.log 2>&1 &
NEURAL_PID=$!
cd ../..

# 3. Start Telegram Bridge (Python)
echo "[*] Starting Telegram Bridge..."
cd services/bridge
$PYTHON_BIN bridge.py > ../../$LOG_DIR/bridge.log 2>&1 &
BRIDGE_PID=$!
cd ../..

# 4. Start Autonomous Monitor
if [ -f "monitor_evolution.sh" ]; then
    echo "[*] Starting Autonomous Evolution Monitor..."
    ./monitor_evolution.sh > /dev/null 2>&1 &
    MONITOR_PID=$!
fi

echo "🚀 Ronaldinho is ready and running in background!"
echo "Check logs in $LOG_DIR/ directory for details."
echo "Press Ctrl+C to stop all services."

trap "kill $SIGNALING_PID $NEURAL_PID $BRIDGE_PID $MONITOR_PID; exit" INT
wait
