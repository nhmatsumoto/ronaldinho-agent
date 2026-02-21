<#
.SYNOPSIS
Script para automatizar a criação do repositório público no GitHub para o Ronaldinho-Agent.

.DESCRIPTION
Este script executa o "gh cli" para inicializar o repositório GIT localmente (caso não tenha),
muda a branch principal para "main", criar o repositório público no GitHub com a licença MIT inclusa (opcional, pode ser adicionada pelo GitHub) 
e, em seguida, faz o push de todos os arquivos atuais.
Requer que o GitHub CLI esteja instalado e autenticado (gh auth login).
#>

param (
    [string]$RepoName = "Ronaldinho-Agent",
    [string]$Description = "Autonomous development ecosystem designed for high performance, security, and self-evolution."
)

Write-Host "Iniciando processo de publicação Open Source do $RepoName..." -ForegroundColor Cyan

# Verifica se o git já está inicializado
if (-not (Test-Path .git)) {
    Write-Host "Inicializando repositório Git..."
    git init
}

# Verificando status e log
git status

# Adicionando todos os arquivos novos, respeitando o .gitignore
Write-Host "Preparando commits..."
git add .
git commit -m "feat: first commit for open source release and project initialization"

# Mudando branch para main
git branch -M main

Write-Host "Criando repositório no GitHub via gh CLI..."
# Usar gh para criar o repo publico, você precisará confirmar algumas etapas se as flags não passarem
# --source=. informa o diretório, --remote=origin fará o setup do remote e push
gh repo create $RepoName --public --description $Description --source=. --remote=origin --push

Write-Host "Repositório criado e arquivos enviados com sucesso para o seu GitHub!" -ForegroundColor Green
Write-Host "Lembre-se de verificar as 'Issues' abertas pela comunidade." -ForegroundColor Yellow
