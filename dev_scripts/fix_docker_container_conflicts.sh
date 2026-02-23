#!/usr/bin/env bash
set -euo pipefail

CONFLICTING_NAMES=(
  ronaldinho_configui
  ronaldinho_neuralcore
  ronaldinho_postgres_keycloak
  ronaldinho_keycloak
  ronaldinho_configui_prod
  ronaldinho_neuralcore_prod
  ronaldinho_postgres_prod
  ronaldinho_keycloak_prod
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

echo "Removing orphaned containers from current compose project (if any)..."
docker compose down --remove-orphans >/dev/null 2>&1 || true

echo "Done. You can now run: docker compose up -d --build --remove-orphans"
