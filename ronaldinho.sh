#!/bin/bash

# Ronaldinho CLI - Inspired by OpenClaw binary
# Purpose: Management and interaction via terminal.

COMMAND=$1
SHIFT_ARG=$2

case $COMMAND in
    "start")
        ./start_ronaldinho.sh
        ;;
    "stop")
        ./stop_ronaldinho.sh
        ;;
    "logs")
        tail -f logs_v1/core.log
        ;;
    "skills")
        echo "--- Ronaldinho Skill Registry ---"
        ls .agent/skills
        ;;
    "install")
        if [ -z "$SHIFT_ARG" ]; then
            echo "Usage: ronaldinho install <skill_name>"
        else
            echo "[*] Simulando download via ClawHub para: $SHIFT_ARG..."
            mkdir -p .agent/skills/$SHIFT_ARG
            touch .agent/skills/$SHIFT_ARG/SKILL.md
            touch .agent/skills/$SHIFT_ARG/main.py
            echo "✅ Skill $SHIFT_ARG initialized."
        fi
        ;;
    "status")
        curl -s http://127.0.0.1:5000/health | jq .
        ;;
    *)
        echo "Ronaldinho AI CLI"
        echo "Usage: ./ronaldinho.sh [start|stop|logs|skills|install|status]"
        ;;
esac
