#!/bin/bash

echo "Starting Keycloak Configuration..."

# Wait for Keycloak to be fully ready
until docker compose exec keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin > /dev/null 2>&1; do
    echo "Waiting for Keycloak to start..."
    sleep 5
done

echo "Keycloak is up. Configuring 'ronaldinho' realm..."

# Authenticate
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin

# Create Realm
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create realms -s realm=ronaldinho -s enabled=true || echo "Realm ronaldinho already exists."

# Create Client for React ConfigUI
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create clients -r ronaldinho -s clientId=configui-client -s enabled=true -s publicClient=true -s 'redirectUris=["http://localhost:5173/*", "http://127.0.0.1:5173/*"]' -s 'webOrigins=["+"]' || echo "Client configui-client already exists."

# Create an Admin User for the operator
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh create users -r ronaldinho -s username=ronaldinho_admin -s enabled=true || echo "User already exists."

# Set Password for the User (password123)
docker compose exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r ronaldinho --username ronaldinho_admin --new-password password123

echo "Keycloak configuration complete."
echo "Login: ronaldinho_admin / password123"
