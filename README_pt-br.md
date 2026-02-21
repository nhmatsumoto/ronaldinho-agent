# Ronaldinho-Agent 🚀 (Edição Open Source)

> [!IMPORTANT]
> **Aviso de Codinome**: "Ronaldinho-Agent" é atualmente um codinome do projeto. Nenhuma marca ou nome oficial foi estabelecido ainda.

[Read this document in English (EN)](README.md)

Ronaldinho-Agent é um ecossistema autônomo de desenvolvimento projetado para altíssima performance, segurança e autoevolução. Impulsionado por um **NeuralCore em .NET 9** e uma **Interface de Governança em React/Chakra UI**, gerencia missões de IA multi-modelo com resiliência nativa e governança determinística.

## 🌟 Nossa Visão: A Força da Comunidade

Inspirado no fenomenal crescimento de plataformas de sucesso global como o **OpenClaw** — cujo potencial técnico e governança atingiram excelência impulsionados pelo trabalho colaborativo e orgânico da comunidade —, o Ronaldinho nasce para ser mais do que apenas um assistente, um ecossistema vivo!

O código sozinho atinge um limite sem a inteligência coletiva. Ao abrirmos esse agente de IA para Open Source, damos as boas-vindas a engenheiros, entusiastas e visionários de todo o mundo. A revolução autônoma é colaborativa.

## 🎯 Objetivos do Projeto

- **Autonomia Nível 6**: A capacidade ininterrupta de auto-início, autocorreção e auto-otimização.
- **Gateway Multi-Modelo**: Suporte nativo para **Gemini 2.0**, **OpenAI (GPT-4o)** e **Claude (Anthropic)**.
- **Resiliência Zero-Block**: Sistema de fallback automático que rotaciona modelos em caso de limites de taxa (erros 429).
- **Interface de Governança**: Dashboard moderno para configuração em tempo real e gestão de chaves de API.
- **Segurança Corporativa**: Autenticação via **Keycloak** com suporte a federação de identidade.
- **Regras Stritas de Execução**: Opera sob a "Unified Execution Doctrine" para determinismo absoluto.

---

## 🚀 Guia de Início Rápido

### Pré-requisitos

- **.NET 9 SDK** (Cérebro Core)
- **Node.js / Bun** (Interface de Governança)
- **Docker & Docker Compose** (Deploy Full Stack)
- **PowerShell 7+** (Scripts de Automação)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/SeuUsuario/Ronaldinho-Agent.git
cd Ronaldinho-Agent

# Configure o ambiente
cp .env.example .env

# Modifique o .env com sua API Key (Nunca submeta chaves para repositórios públicos!)
```

### Início Rápido (Local)

```powershell
# Windows (PowerShell)
./start_neural.ps1
```

```bash
# Linux / macOS (Bash)
chmod +x start_neural.sh ./dev_scripts/*.sh
./start_neural.sh
```

### Stack Completa (Docker)

```bash
# Sobe o Cérebro, UI, Keycloak e Banco de Dados
docker compose up -d --build
```

---

## 🤝 Como Contribuir e Ajudar o Ronaldinho a Crescer

Assim como percebido brilhantemente com o OpenClaw, nós apostamos tudo nas contribuições! Desde novos scripts `dev_scripts` à melhorias estruturais no *Orquestrador*:

1. Realize um **Fork** do repositório.
2. Siga as cruciais **Regras de Governança Local** ao criar suas features.
3. Se você identificar ações manuais recorrentes, crie ferramentas em `.toolbox` ou `dev_scripts/`.
4. Trabalhe na sua **Branch** (`git checkout -b feature/SuaInovacao`).
5. Gere os Testes Locais com a validação do TOON e escreva logs.
6. Envie o seu **Pull Request** para a *main* / *master*.
  
A comunidade analisará cada submissão. Cuidado com o vazamento de chaves ou dependências não catalogadas.

---

## 📜 Licença

Distribuído sob a Licença **MIT**. Veja o arquivo `LICENSE` para maiores detalhes.
