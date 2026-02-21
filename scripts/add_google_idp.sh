#!/bin/bash
# Usage: ./add_google_idp.sh <CLIENT_ID> <CLIENT_SECRET>

CLIENT_ID=$1
CLIENT_SECRET=$2

if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo "Usage: ./add_google_idp.sh <CLIENT_ID> <CLIENT_SECRET>"
    exit 1
fi

echo "Adding Google Identity Provider to Ronaldinho realm..."

# Authenticate (assumes admin/admin123 based on recent reset)
docker exec ronaldinho_keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin123

# Create Identity Provider
docker exec ronaldinho_keycloak /opt/keycloak/bin/kcadm.sh create identity-provider/instances -r ronaldinho \
    -s alias=google \
    -s providerId=google \
    -s enabled=true \
    -s 'config={"clientId":"'$CLIENT_ID'","clientSecret":"'$CLIENT_SECRET'","useJwksUrl":"true"}'

echo "Google Identity Provider added successfully."
