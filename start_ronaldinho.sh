#!/bin/bash

# Ronaldinho Agent: Unified Launcher (Background Edition)

echo "🏀 Ronaldinho Agent is starting (Pure Background Mode)..."

# Pre-flight: Kill any existing processes on ports 3000 and 5000
echo "[*] Cleaning up old processes..."
fuser -k 3000/tcp 5000/tcp > /dev/null 2>&1

# 0. Check Virtual Environment and Logs
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r src/core/requirements.txt"
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
cd src/core
$PYTHON_BIN main.py > ../../$LOG_DIR/core.log 2>&1 &
NEURAL_PID=$!
cd ../..

# 3. Start Telegram Bridge (Python)
echo "[*] Starting Telegram Bridge..."
cd src/bridge
$PYTHON_BIN main.py > ../../$LOG_DIR/bridge.log 2>&1 &
BRIDGE_PID=$!
cd ../..

# 4. Start Web Dashboard (Python HTTP Server)
echo "[*] Starting Web Dashboard on http://localhost:3000..."
cd src/web
$PYTHON_BIN -m http.server 3000 > ../../$LOG_DIR/web.log 2>&1 &
WEB_PID=$!
cd ../..

# 5. Start Autonomous Monitor
if [ -f "monitor_evolution.sh" ]; then
    echo "[*] Starting Autonomous Evolution Monitor..."
    ./monitor_evolution.sh > /dev/null 2>&1 &
    MONITOR_PID=$!
fi

echo "🚀 Ronaldinho is ready and running in background!"
echo "Dashboard: http://localhost:3000"
echo "Neural Core: http://localhost:5000"
echo "Check logs in $LOG_DIR/ directory for details."
echo "Press Ctrl+C to stop all services."

trap "kill $SIGNALING_PID $NEURAL_PID $BRIDGE_PID $WEB_PID $MONITOR_PID 2>/dev/null; exit" INT
wait
