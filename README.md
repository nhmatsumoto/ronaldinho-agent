# Ronaldinho-Agent 🚀 (Open Source Edition)

> [!IMPORTANT]
> **Codename Disclaimer**: "Ronaldinho-Agent" is currently a project codename. No official brand or naming has been established yet.

[Leia este documento em Português (PT-BR)](README_pt-br.md)

Ronaldinho-Agent is an autonomous development ecosystem designed for high performance, security, and self-evolution. Powered by a **.NET 9 NeuralCore** and a **React/Chakra UI Governance Interface**, it manages multi-model AI missions with built-in resilience and deterministic governance.

## 🌟 Our Vision: The Power of Community

Inspired by the phenomenal growth of successful global open-source platforms like **OpenClaw** — whose technical potential and governance reached excellence driven by organic, collaborative community work — Ronaldinho was born to be more than just an assistant; it's a living ecosystem!

Code alone reaches a limit without collective intelligence. By opening this AI agent to open source, we welcome engineers, enthusiasts, and visionaries from all over the world. The autonomous revolution is collaborative.

## 🎯 Project Objectives

- **Level 6 Autonomy**: The continuous capacity for self-starting, self-correction, and self-optimization.
- **Multi-Model Gateway**: Native support for **Gemini 2.0**, **OpenAI (GPT-4o)**, and **Claude (Anthropic)**.
- **Zero-Block Resilience**: Automatic fallback system that rotates models on rate limits (429 errors).
- **Governance UI**: Modern dashboard for real-time configuration and API key management.
- **Enterprise Security**: Authentication powered by **Keycloak** with identity federation.
- **Strict Execution Rules**: Operates based on the "Unified Execution Doctrine" for absolute determinism.

---

## 🚀 Quick Start

### Prerequisites

- **.NET 9 SDK** (Core Engine)
- **Node.js / Bun** (Governance UI)
- **Docker & Docker Compose** (Full Stack Deployment)
- **PowerShell 7+** (Automation Scripts)

### Installation

```bash
# Clone the repository
git clone https://github.com/nhmatsumoto/Ronaldinho-Agent.git
cd Ronaldinho-Agent

# Set up the environment
cp .env.example .env

# Modify .env with your API Key (Never submit keys to public repositories!)
```

### Quick Boot (Local)

```powershell
# Windows (PowerShell)
./start_neural.ps1
```

```bash
# Linux / macOS (Bash)
chmod +x start_neural.sh ./dev_scripts/*.sh
./start_neural.sh
```

### Full Stack (Docker)

```bash
# Deploys Brain, UI, Keycloak, and Database
docker compose up -d --build
```

---

## 🤝 How to Contribute and Help Ronaldinho Grow

Just as brilliantly perceived with OpenClaw, we bet everything on contributions! From new `dev_scripts` to structural improvements in the *Orchestrator*:

1. Fork the repository.
2. Follow the crucial **Local Governance Rules** when creating your features.
3. If you identify recurring manual actions, create tools in `.toolbox` or `dev_scripts/`.
4. Work on your **Branch** (`git checkout -b feature/YourInnovation`).
5. Generate Local Tests with TOON validation and write logs.
6. Submit your **Pull Request** to the *main* / *master* branch.

The community will analyze every submission. Be careful with key leaks or uncatalogued dependencies.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more details.
