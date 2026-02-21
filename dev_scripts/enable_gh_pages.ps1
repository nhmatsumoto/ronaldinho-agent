<#
.SYNOPSIS
Script para publicar as alterações preparando o repositório para o GitHub Pages.

.DESCRIPTION
Como o GitHub CLI (gh) não está instalado no ambiente atual, este script
apenas garante que todas as alterações locais sob a pasta /docs sejam 
devidamente commitadas e enviadas (push) para a branch atual (master ou main).
A ativação final deverá ser feita manualmente pelo painel do repositório no GitHub.
#>

Write-Host "Preparando os arquivos da Landing Page para publicação..." -ForegroundColor Cyan

# Adicionando garantidamente todas as alterações
git add .

# Salvando a alteração commitando 
# (Silencia erro caso não haja nada novo para comitar)
$commitOutput = git commit -m "docs: publish github pages landing page" 2>&1
if ($commitOutput -match "nothing to commit") {
    Write-Host "Todas as alterações já foram encapsuladas nos commits anteriores." -ForegroundColor Yellow
} else {
    Write-Host "Nova versão commitada com sucesso." -ForegroundColor Green
}

# Realizando push para a origem na branch atual
Write-Host "Enviando para o GitHub..."
# Extrai o nome da branch atual
$branch = git branch --show-current
git push origin $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "=============================" -ForegroundColor Green
    Write-Host "✅ Arquivos enviados com sucesso para a branch '$branch'!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Como o 'gh CLI' não está instalado nesta máquina, para ativar o GitHub Pages, por favor faça:" -ForegroundColor Yellow
    Write-Host "1. Abra https://github.com/nhmatsumoto/Ronaldinho-Agent/settings/pages" -ForegroundColor Yellow
    Write-Host "2. Na seção 'Build and deployment', escolha 'Deploy from a branch'" -ForegroundColor Yellow
    Write-Host "3. Abaixo de 'Branch', selecione '$branch' e a pasta '/docs', depois clique em 'Save'" -ForegroundColor Yellow
    Write-Host "=============================" -ForegroundColor Green
} else {
    Write-Host "Falha ao enviar os arquivos para o repositório remoto. Verifique o status da rede e permissões." -ForegroundColor Red
}
