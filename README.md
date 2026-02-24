# Ronaldinho-Agent 🚀

Ronaldinho-Agent is an autonomous engineering ecosystem designed for high performance and self-evolution.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([User]) --> |Telegram| Bridge[Python Bridge]
    User --> |Browser| Dashboard[Web Dashboard]

    subgraph "Core Ecosystem"
        Bridge <--> Core[Python NeuralCore]
        Dashboard <--> Core
        Core --> Vault[(Secure Token Vault)]
        Core --> Bench[Model Benchmarker]
    end

    subgraph "AI Providers"
        Core --> Gemini[Google Gemini]
        Core --> OpenAI[OpenAI]
        Core --> NVIDIA[NVIDIA NIM]
        Core --> Local[Local Gemini CLI]
    end

    Bench -.-> |Integrity Check| Gemini
    Bench -.-> |Integrity Check| OpenAI
```

---

## 🛠️ Getting Started

### 1. Prerequisites

- **Python 3.10+**
- **Docker & Docker Compose** (optional)
- **Telegram Bot Token** (obtained via [@BotFather](https://t.me/botfather))

### 2. Environment Configuration

Create a `.env` file in the root directory (use `.env.example` as a template):

```bash
cp .env.example .env
```

### 3. Local Execution (Quick Start)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r services/core/requirements.txt
chmod +x start_ronaldinho.sh
./start_ronaldinho.sh
```

---

## 🖥️ Web Dashboard & OAuth2 Flow

Ronaldinho uses a modern authentication flow to manage your AI credentials securely.

### Connection Flow

```mermaid
sequenceDiagram
    participant U as User
    participant D as Dashboard
    participant C as NeuralCore
    participant P as AI Provider
    participant V as Vault

    U->>D: Click "Connect"
    D->>C: GET /api/auth/login
    C-->>D: Authorization URL
    D->>P: Redirect to Login
    P-->>D: Return with Auth Code
    D->>C: GET /api/auth/callback?code=...
    C->>P: Exchange Code for Token
    P-->>C: Access Token
    C->>V: Encrypt and Save Token
    V-->>C: Success
    C-->>D: Status: Connected
```

---

## 🧠 Intelligence and Resilience

### Model Selection (Integrity Logic)

Ronaldinho doesn't just "ping" providers; it tests the functional capability of each model before selecting it.

```mermaid
graph LR
    Start[Request Start] --> CheckVault{Token in Vault?}
    CheckVault -->|Yes| UseVault[Use Personal Token]
    CheckVault -->|No| UseEnv[Use .env Key]

    UseVault --> Bench[Benchmarker: Test Latency/Integrity]
    UseEnv --> Bench

    Bench --> Best{Which is best?}
    Best -->|Online| Model[Execute with Fast Model]
    Best -->|Failure| Local[Fallback: Local Gemini CLI]
```

---

## 📂 Repository Structure

```text
.
├── services/
│   ├── core/                # Brain & Manus Tools (FastAPI)
│   ├── bridge/              # Telegram Bridge (Python)
│   └── web/                 # Dashboard Web (OIDC/OAuth2)
├── ronaldinho/              # Soul & Secure Vault
├── logs_v1/                 # Execution logs
└── start_ronaldinho.sh      # Unified Launcher
```

License: **MIT**
