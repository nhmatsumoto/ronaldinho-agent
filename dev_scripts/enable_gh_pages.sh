#!/bin/bash

# Script para publicar as alterações preparando o repositório para o GitHub Pages.

echo -e "\e[36mPreparando os arquivos da Landing Page para publicação...\e[0m"

# Adicionando garantidamente todas as alterações
git add .

# Salvando a alteração commitando 
# (Silencia erro caso não haja nada novo para comitar)
commit_output=$(git commit -m "docs: publish github pages landing page" 2>&1)

if [[ $commit_output == *"nothing to commit"* ]]; then
    echo -e "\e[33mTodas as alterações já foram encapsuladas nos commits anteriores.\e[0m"
else
    echo -e "\e[32mNova versão commitada com sucesso.\e[0m"
fi

# Realizando push para a origem na branch atual
echo "Enviando para o GitHub..."
branch=$(git branch --show-current)
git push origin "$branch"

if [ $? -eq 0 ]; then
    echo -e "\e[32m=============================\e[0m"
    echo -e "\e[32m✅ Arquivos enviados com sucesso para a branch '$branch'!\e[0m"
    echo ""
    echo -e "\e[33mComo o 'gh CLI' não está instalado nesta máquina, para ativar o GitHub Pages, por favor faça:\e[0m"
    echo -e "\e[33m1. Abra https://github.com/nhmatsumoto/Ronaldinho-Agent/settings/pages\e[0m"
    echo -e "\e[33m2. Na seção 'Build and deployment', escolha 'Deploy from a branch'\e[0m"
    echo -e "\e[33m3. Abaixo de 'Branch', selecione '$branch' e a pasta '/docs', depois clique em 'Save'\e[0m"
    echo -e "\e[32m=============================\e[0m"
else
    echo -e "\e[31mFalha ao enviar os arquivos para o repositório remoto. Verifique o status da rede e permissões.\e[0m"
fi
