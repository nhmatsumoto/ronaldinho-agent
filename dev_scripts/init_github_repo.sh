#!/bin/bash

# Script para automatizar a criação do repositório público no GitHub para o Ronaldinho-Agent.

REPO_NAME=${1:-"Ronaldinho-Agent"}
DESCRIPTION=${2:-"Autonomous development ecosystem designed for high performance, security, and self-evolution."}

echo -e "\e[36mIniciando processo de publicação Open Source do $REPO_NAME...\e[0m"

# Verifica se o git já está inicializado
if [ ! -d ".git" ]; then
    echo "Inicializando repositório Git..."
    git init
fi

# Verificando status e log
git status

# Adicionando todos os arquivos novos, respeitando o .gitignore
echo "Preparando commits..."
git add .
git commit -m "feat: first commit for open source release and project initialization"

# Mudando branch para main
git branch -M main

echo "Criando repositório no GitHub via gh CLI..."
# Usar gh para criar o repo publico, você precisará confirmar algumas etapas se as flags não passarem
# --source=. informa o diretório, --remote=origin fará o setup do remote e push
gh repo create "$REPO_NAME" --public --description "$DESCRIPTION" --source=. --remote=origin --push

echo -e "\e[32mRepositório criado e arquivos enviados com sucesso para o seu GitHub!\e[0m"
echo -e "\e[33mLembre-se de verificar as 'Issues' abertas pela comunidade.\e[0m"
