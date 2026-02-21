<#
.SYNOPSIS
Script para habilitar a configuração do GitHub Pages no repositório remoto via gh CLI.

.DESCRIPTION
Como os agentes possuem regras restritas de acesso a browser e APIs externas de terceiros de forma autônoma,
este script utiliza a ferramenta GitHub CLI já autenticada localmente pelo desenvolvedor para disparar 
a ativação do GitHub Pages apontando para a branch 'main', no diretório '/docs', via chamadas REST da API do GitHub.
#>

Write-Host "Iniciando a ativação do GitHub Pages..." -ForegroundColor Cyan

# Verifica qual é o repositório atual
$repo = gh repo view --json nameWithOwner -q .nameWithOwner
if ([string]::IsNullOrWhiteSpace($repo)) {
    Write-Host "ERRO: Repositório GitHub remoto não encontrado ou CLI não logado (gh auth login)." -ForegroundColor Red
    exit 1
}

Write-Host "Repositório detectado: $repo" -ForegroundColor Cyan
Write-Host "Configurando Pages para buildar a partir de main:/docs ..."

# Chama a API do GitHub para criar a configuração Pages
# O POST espera source[branch] e source[path]
gh api -X POST /repos/$repo/pages `
    -f source[branch]=main `
    -f source[path]=/docs 

# Verificando se deu certo (ignorando possíveis restrições de já existente dependendo do erro retornado verbalmente)
if ($LASTEXITCODE -eq 0) {
    Write-Host "=============================" -ForegroundColor Green
    Write-Host "✅ GitHub Pages CONFIGURADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "Ele deve estar disponível online dentro de alguns instantes (https://$(($repo -split '/')[0]).github.io/$(($repo -split '/')[1]))." -ForegroundColor Yellow
    Write-Host "=============================" -ForegroundColor Green
} else {
    Write-Host "Ocorreu um erro ao configurar. Leia a mensagem do GitHub logo acima." -ForegroundColor Yellow
}
