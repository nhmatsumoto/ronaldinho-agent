# Ronaldinho-Agent 🚀 (Open Source Edition)

> [!IMPORTANT]
> **Aviso de codinome**: "Ronaldinho-Agent" é um codinome de projeto. Ainda não há naming oficial de produto.

[Versão PT-BR anterior](README_pt-br.md)

O **Ronaldinho-Agent** é um ecossistema de agente autônomo com:
- **NeuralCore em .NET 9** (orquestração e API),
- **Bridge worker** para integração com Telegram,
- **ConfigUI em React + Vite + Chakra UI** para governança,
- **Keycloak + Postgres** para autenticação OIDC no fluxo de configuração.

Este README foi estruturado para você conseguir: **entender arquitetura**, **rodar localmente**, **subir com Docker**, e **desenvolver/contribuir** com segurança.

---

## 📚 Sumário

- [1) Visão geral da arquitetura](#1-visão-geral-da-arquitetura)
- [2) Estrutura do repositório](#2-estrutura-do-repositório)
- [3) Pré-requisitos](#3-pré-requisitos)
- [4) Configuração de ambiente (.env)](#4-configuração-de-ambiente-env)
- [5) Como executar](#5-como-executar)
  - [5.1 Execução local rápida](#51-execução-local-rápida)
  - [5.2 Execução manual por serviço (dev)](#52-execução-manual-por-serviço-dev)
  - [5.3 Execução full stack com Docker](#53-execução-full-stack-com-docker)
- [6) API e autenticação](#6-api-e-autenticação)
- [7) Desenvolvimento](#7-desenvolvimento)
- [8) Scripts utilitários](#8-scripts-utilitários)
- [9) Segurança e boas práticas](#9-segurança-e-boas-práticas)
- [10) Troubleshooting](#10-troubleshooting)
- [11) Documentação complementar](#11-documentação-complementar)
- [12) Contribuição e licença](#12-contribuição-e-licença)

---

## 1) Visão geral da arquitetura

### Componentes principais

1. **NeuralCore (`services/Ronaldinho.NeuralCore`)**
   - API HTTP (porta `5000`) e cérebro de orquestração.
   - Carrega variáveis de ambiente de um arquivo `.env` na raiz.
   - Aplica autenticação JWT/OIDC com Keycloak para endpoints protegidos.

2. **Bridge (`services/Ronaldinho.Bridge`)**
   - Worker .NET que conecta o runtime ao Telegram.
   - Lê token do Telegram do vault local ou variável de ambiente.

3. **ConfigUI (`services/Ronaldinho.ConfigUI`)**
   - Frontend React/Vite (porta `5173` em desenvolvimento).
   - Faz login via OIDC (Keycloak) e persiste configurações no backend.

4. **Keycloak + Postgres (via Docker Compose)**
   - Camada de identidade/autorização para a UI e API.

### Fluxo simplificado

- Você sobe o NeuralCore.
- Se o ambiente ainda não estiver configurado (sem token/chaves), a UI é usada para setup inicial.
- Após configuração, o bridge pode iniciar e processar mensagens Telegram.

---

## 2) Estrutura do repositório

```text
.
├── services/
│   ├── Ronaldinho.NeuralCore/   # API e orquestração principal (.NET 9)
│   ├── Ronaldinho.Bridge/       # Worker/integração Telegram (.NET 9)
│   └── Ronaldinho.ConfigUI/     # Frontend de governança (React + Vite)
├── ronaldinho/
│   ├── config/                  # SOUL.md e configs comportamentais
│   └── data/                    # vault local/artefatos de segurança
├── dev_scripts/                 # scripts utilitários para dev/start
├── scripts/                     # scripts de configuração Keycloak/IDP
├── docs/                        # documentação técnica e funcional
├── docker-compose.yml           # stack de desenvolvimento
├── docker-compose.prod.yml      # stack de produção
├── start_neural.sh              # bootstrap Linux/macOS
└── start_neural.ps1             # bootstrap Windows
```

---

## 3) Pré-requisitos

### Para desenvolvimento local

- **.NET SDK 9.0**
- **Node.js 18+** (npm) *ou* Bun (opcional)
- **PowerShell 7+** (se usar scripts `.ps1`)
- **Git**

### Para stack completa

- **Docker**
- **Docker Compose**

---

## 4) Configuração de ambiente (.env)

> [!WARNING]
> Atualmente o repositório **não inclui `.env.example`**. Crie manualmente um arquivo `.env` na raiz.

Exemplo mínimo sugerido:

```env
# LLM e Telegram
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
TELEGRAM_BOT_TOKEN=
LLM_PROVIDER=gemini
ENABLE_AUTO_FALLBACK=true
ALLOW_LOCAL_TOOLS=false

# Auth (Keycloak / OIDC)
AUTH_AUTHORITY=http://localhost:8080/realms/ronaldinho
AUTH_AUDIENCE=account

# ConfigUI (Vite)
VITE_AUTH_AUTHORITY=http://localhost:8080/realms/ronaldinho
VITE_AUTH_CLIENT_ID=configui-client
VITE_AUTH_REDIRECT_URI=http://localhost:5173

# Banco do Keycloak (Docker)
DB_NAME=keycloak
DB_USER=keycloak
DB_PASSWORD=password
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin
KC_HOSTNAME=localhost
```

### Observações

- Para rodar setup inicial pela UI, o backend pode subir mesmo sem `TELEGRAM_BOT_TOKEN`.
- O `start_neural` considera “configurado” quando há token Telegram e ao menos 1 chave de LLM válida.
- Nunca commite secrets reais no Git.

---

## 5) Como executar

## 5.1 Execução local rápida

### Linux/macOS

```bash
chmod +x start_neural.sh ./dev_scripts/*.sh
./start_neural.sh
```

### Windows (PowerShell)

```powershell
./start_neural.ps1
```

Esse bootstrap:
- inicia o **NeuralCore**,
- verifica se ambiente está configurado,
- se estiver, inicia o **Bridge**,
- se não estiver, sobe a **ConfigUI** para setup inicial.

## 5.2 Execução manual por serviço (dev)

### Terminal 1 — NeuralCore

```bash
dotnet run --project services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj
```

### Terminal 2 — Bridge (opcional)

```bash
dotnet run --project services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj
```

### Terminal 3 — ConfigUI

```bash
cd services/Ronaldinho.ConfigUI
npm install
npm run dev
```

Acessos locais:
- API NeuralCore: `http://localhost:5000`
- ConfigUI: `http://localhost:5173`
- Keycloak (se via Docker): `http://localhost:8080`

## 5.3 Execução full stack com Docker

```bash
docker compose up -d --build
```

Serviços incluídos no compose de desenvolvimento:
- `ronaldinho-neuralcore`
- `ronaldinho-configui`
- `postgres_keycloak`
- `keycloak`

Para produção:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 6) API e autenticação

### Endpoints principais

- `GET /api/settings` (protegido por autenticação)
- `POST /api/settings` (protegido por autenticação)

O backend usa JWT Bearer com autoridade/audience baseados em:
- `AUTH_AUTHORITY`
- `AUTH_AUDIENCE`

A UI usa variáveis `VITE_AUTH_*` para login OIDC no Keycloak.

---

## 7) Desenvolvimento

### Build/check rápido

#### Backend

```bash
dotnet build services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj
dotnet build services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj
```

#### Frontend

```bash
cd services/Ronaldinho.ConfigUI
npm run lint
npm run build
```

### Fluxo recomendado

1. Crie uma branch de feature/fix.
2. Faça mudanças pequenas e com contexto claro.
3. Rode build/lint local antes de abrir PR.
4. Evite dependências não catalogadas e exposição de segredos.

---

## 8) Scripts utilitários

### `dev_scripts/`

- `start_ui.sh` / `start_ui.ps1`: sobe apenas a ConfigUI.
- `start_ronaldinho.sh` / `start_ronaldinho.ps1`: wrappers de inicialização.
- `kill_ronaldinho.ps1`: auxilia encerramento no Windows.
- `fix_docker_registry.ps1`, `reset_keycloak_admin.ps1`, etc.: manutenção operacional.

### `scripts/`

- `setup_keycloak.sh`: cria realm/client/user iniciais no Keycloak.
- `add_google_idp.sh`: registra Google como IdP no realm.
- `add_github_idp.sh`: registra GitHub como IdP no realm.

> [!NOTE]
> Alguns scripts assumem credenciais padrão específicas; revise antes de usar em ambientes reais.

---

## 9) Segurança e boas práticas

- Não versione `.env`, tokens, segredos ou dumps sensíveis.
- Revise `SECURITY.md` e `docs/security_model.md`.
- Em PRs, remova dados sensíveis de logs e screenshots.
- Prefira credenciais específicas de ambiente, com rotação periódica.

---

## 10) Troubleshooting

### “.NET SDK not found”
Instale .NET 9 e confirme:

```bash
dotnet --version
```

### “Project file not found”
Rode comandos na raiz do repositório (`/workspace/ronaldinho-agent`).

### UI não sobe em `:5173`
Entre em `services/Ronaldinho.ConfigUI`, instale dependências e rode `npm run dev`.

### Erro de autenticação OIDC
Verifique:
- realm/client no Keycloak,
- `AUTH_AUTHORITY`, `AUTH_AUDIENCE`,
- `VITE_AUTH_AUTHORITY`, `VITE_AUTH_CLIENT_ID`, `VITE_AUTH_REDIRECT_URI`.

### Bridge não conecta no Telegram
Confirme `TELEGRAM_BOT_TOKEN` e se o token foi salvo corretamente via UI/vault.

---

## 11) Documentação complementar

- `docs/architecture.md`
- `docs/security_model.md`
- `docs/mission_lifecycle.md`
- `docs/integration_roadmap.md`
- `CONTRIBUTING.md`

---

## 12) Contribuição e licença

Contribuições são bem-vindas via PR.

Antes de contribuir, leia:
- `CONTRIBUTING.md`
- `SECURITY.md`

Licença: **MIT** (`LICENSE`).
