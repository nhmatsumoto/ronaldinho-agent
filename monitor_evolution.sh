#!/bin/bash
LOG_CORE="logs_v1/core.log"
LOG_BRIDGE="logs_v1/bridge.log"
echo "[*] Ronaldinho Watchdog: Monitoring for errors and conflicts..."
while true; do
  ERRORS=$(grep -E "Error|500|503|Exception|[ $LOG_CORE $LOG_BRIDGE | tail -n 5)
  if [ ! -z "$ERRORS" ]; then
    echo "$(date): [!] Anomaly detected:"
    echo "$ERRORS"
  fi
  sleep 10
done
