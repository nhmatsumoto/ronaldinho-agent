#!/bin/bash

# Ronaldinho Keycloak Hard Reset
# This script wipes the Keycloak database to restore default admin access (admin/admin).

echo -e "\e[33m⚠️ Iniciando Reset Forçado do Keycloak...\e[0m"

# 1. Stop Keycloak and Database
echo -e "\e[90m[*] Parando containers do Keycloak e Postgres...\e[0m"
docker compose stop keycloak postgres_keycloak

# 2. Remove the Postgres Volume
echo -e "\e[31m[!] Removendo volume de dados do Postgres (isso resetará as senhas)...\e[0m"
# Try with common prefixes or the current directory name
docker volume rm ronaldinho-agent_postgres_keycloak_data 2>/dev/null
docker volume rm postgres_keycloak_data 2>/dev/null

# 3. Start again
echo -e "\e[36m[*] Reiniciando containers... Aguarde a inicialização.\e[0m"
docker compose up -d keycloak postgres_keycloak

echo -e "\n\e[32m✅ Keycloak resetado!\e[0m"
echo "Aguarde cerca de 30-60 segundos e tente o login novamente em:"
echo "http://localhost:8080/admin/master/console/"
echo -e "Usuário: admin | Senha: \e[36madmin\e[0m"
