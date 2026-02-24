# Ronaldinho-Agent 🚀

Ronaldinho-Agent é um ecossistema de engenharia autônomo composto por:

- **Python NeuralCore**: O cérebro evolutivo (FastAPI + PydanticAI).
- **Integração Multi-Modelos**: Troca dinâmica entre Gemini, NVIDIA, OpenAI, Anthropic e Groq com testes de integridade em tempo real.
- **Python Bridge**: Integração com Telegram e processamento de eventos.
- **Web Dashboard**: Interface para gestão de conexões OAuth2 e monitoramento.

---

## 🛠️ Como Rodar o Projeto

### 1. Pré-requisitos

- **Python 3.10+**
- **Docker & Docker Compose** (opcional, para rodar via containers)
- **Telegram Bot Token** (obtido via [@BotFather](https://t.me/botfather))

### 2. Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base):

```bash
cp .env.example .env
# Edite as chaves conforme necessário (TELEGRAM_BOT_TOKEN, etc.)
```

### 3. Execução Local (Recomendado para Dev)

#### Passo A: Preparar o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r services/core/requirements.txt
```

#### Passo B: Iniciar todos os serviços

Use o script unificado que inicia o Signaling Server, NeuralCore e Bridge em background:

```bash
chmod +x start_ronaldinho.sh
./start_ronaldinho.sh
```

### 4. Execução via Docker

Se preferir isolamento total:

```bash
docker-compose up --build
```

---

## 🖥️ Web Dashboard & OAuth2

O Ronaldinho agora possui um Dashboard Web para facilitar a conexão com provedores sem precisar editar o `.env` manualmente.

1. Com o **NeuralCore** rodando (porta 5000), abra o arquivo `services/web/index.html` no seu navegador.
2. No painel de **Conexões**, clique em "Conectar OpenAI" ou "Conectar Gemini".
3. Siga o fluxo OAuth2 para autorizar o Ronaldinho.
4. As chaves serão salvas de forma segura e criptografada no seu cofre local (`ronaldinho/vault.json`).

---

## 🧠 Recursos Avançados

### Teste de Integridade de Modelos

O Ronaldinho testa automaticamente a validade das chaves e a disponibilidade dos modelos. Você pode rodar o benchmarker manualmente para ver o status atual:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/services/core
python3 services/core/app/benchmarker.py
```

### Fallback "Local Gemini CLI"

Em caso de falha total nas APIs externas, o Ronaldinho utiliza um wrapper direto (`app/gemini_cli_local.py`) para garantir que o serviço nunca fique offline.

---

## 📂 Estrutura do Repositório

```text
.
├── services/
│   ├── core/                # Brain & Manus Tools (FastAPI)
│   ├── bridge/              # Telegram Bridge (Python)
│   └── web/                 # Dashboard Web (HTML/JS/CSS)
├── ronaldinho/              # Cofre de Segredos (vault.json) & Soul
├── logs_v1/                 # Logs de execução
└── start_ronaldinho.sh      # Launcher Unificado
```

License: **MIT**
