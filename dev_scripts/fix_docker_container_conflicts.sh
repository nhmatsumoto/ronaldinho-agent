#!/usr/bin/env bash
set -euo pipefail

CONFLICTING_NAMES=(
  ronaldinho_configui
  ronaldinho_neuralcore
  ronaldinho_postgres_keycloak
  ronaldinho_keycloak
)

echo "Checking for stale containers with legacy fixed names..."
for name in "${CONFLICTING_NAMES[@]}"; do
  if docker container inspect "$name" >/dev/null 2>&1; then
    echo "Removing existing container: $name"
    docker rm -f "$name" >/dev/null
  else
    echo "Not found: $name"
  fi
done

echo "Done. You can now run: docker compose up -d --build"
