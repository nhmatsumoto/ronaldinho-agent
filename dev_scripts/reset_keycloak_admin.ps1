# Ronaldinho Keycloak Hard Reset
# This script wipes the Keycloak database to restore default admin access (admin/admin).

Write-Host "⚠️ Iniciando Reset Forçado do Keycloak..." -ForegroundColor Yellow

# 1. Stop Keycloak and Database
Write-Host "[*] Parando containers do Keycloak e Postgres..." -ForegroundColor Gray
docker compose stop keycloak postgres_keycloak

# 2. Remove the Postgres Volume
Write-Host "[!] Removendo volume de dados do Postgres (isso resetará as senhas)..." -ForegroundColor Red
docker volume rm ronaldinho-agent_postgres_keycloak_data 2>$null
# Try without the prefix just in case
docker volume rm postgres_keycloak_data 2>$null

# 3. Start again
Write-Host "[*] Reiniciando containers... Aguarde a inicialização." -ForegroundColor Cyan
docker compose up -d keycloak postgres_keycloak

Write-Host "`n✅ Keycloak resetado!" -ForegroundColor Green
Write-Host "Aguarde cerca de 30-60 segundos e tente o login novamente em:"
Write-Host "http://localhost:8080/admin/master/console/"
Write-Host "Usuário: admin | Senha: admin" -ForegroundColor Cyan
