#!/bin/bash
LOG_CORE="logs_v1/core.log"
LOG_BRIDGE="logs_v1/bridge.log"
echo "[*] Ronaldinho Watchdog: Monitoring for errors and conflicts..."
while true; do
  if [ -f "$LOG_CORE" ] || [ -f "$LOG_BRIDGE" ]; then
    ERRORS=$(grep -E "Error|500|503|Exception|Conflict" "$LOG_CORE" "$LOG_BRIDGE" 2>/dev/null | tail -n 5)
    if [ ! -z "$ERRORS" ]; then
      echo "$(date): [!] Anomaly detected:"
      echo "$ERRORS"
    fi
  fi
  sleep 30
done
