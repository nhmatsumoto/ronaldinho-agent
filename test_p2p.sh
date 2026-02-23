#!/bin/bash

# Script to launch two Ronaldinho instances for P2P testing

# Kill existing dotnet processes if any (optional, be careful)
# pkill dotnet
echo "🔨 Building project..."
dotnet build services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj

# 1. Start signaling server in background
echo "🚀 Starting P2P Signaling Server (Python/Standard Lib)..."
python3 -u signaling_server.py > signaling.log 2>&1 &
SIGNAL_PID=$!

# Small delay to ensure signaling server is up
sleep 2

# 2. Launch instances with absolute logs for debugging
echo "⚽ Launching Instance A on port 5000 (Data: ronaldinho_a) ⚽"
export PORT=5000
export DATA_DIR=ronaldinho_a
export P2P_LOCAL_ID=peer-a
export P2P_REMOTE_ID=peer-b
export P2P_SIGNALING=http://127.0.0.1:3000
export P2P_INITIATOR=true
dotnet run --no-build --project services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj > instance_a.log 2>&1 &
PID_A=$!

echo "⚽ Launching Instance B on port 5001 (Data: ronaldinho_b) ⚽"
export PORT=5001
export DATA_DIR=ronaldinho_b
export P2P_LOCAL_ID=peer-b
export P2P_REMOTE_ID=peer-a
export P2P_SIGNALING=http://127.0.0.1:3000
export P2P_INITIATOR=false
dotnet run --no-build --project services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj > instance_b.log 2>&1 &
PID_B=$!

echo "All services are starting..."
echo "Instance A: http://localhost:5000 (Log: instance_a.log)"
echo "Instance B: http://localhost:5001 (Log: instance_b.log)"
echo "Signaling: http://127.0.0.1:3000 (Log: signaling.log)"
echo "Press Ctrl+C to stop all."

# 3. Wait and cleanup
trap "kill $PID_A $PID_B $SIGNAL_PID; exit" INT
wait
