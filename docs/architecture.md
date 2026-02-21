# Project Architecture

Ronaldinho-Agent follows a modern, hyper-converged architecture where a C# NeuralCore orchestrates diverse AI strategies and governance rules.

## Directory Structure

```text
Ronaldinho-Agent/
├── services/
│   ├── Ronaldinho.NeuralCore/    # .NET 9 Central Brain & API
│   ├── Ronaldinho.ConfigUI/      # React/Chakra UI Governance Interface
├── ronaldinho/                   # Core Data & Persistent State
│   ├── config/                   # SOUL.md and state definitions
│   ├── data/                     # Encryption keys and vault
├── dev_scripts/                  # PowerShell automation (Smart Onboarding)
├── docs/                         # Technical documentation
├── start_neural.ps1              # Unified Local Entry Point
└── docker-compose.yml            # Containerized Deployment (Production)
```

## Key Components

### 1. NeuralCore (The Master Brain)

A high-performance **.NET 9** engine that utilizes **Semantic Kernel** to coordinate multiple LLM strategies. It handles:
- **Provider Rotation**: Implements the **Zero-Block Resilience** chain.
- **MCP Protocol**: Multi-Agent Coordination for specialized tasks.

### 2. Zero-Block Resilience Chain
Ronaldinho never stays silent. If a primary provider (e.g., Gemini) returns a **429 (Rate Limit)**, the system automatically rotates the brain:
`Gemini 2.0` ➔ `OpenAI (GPT-4o)` ➔ `Claude (Anthropic)` ➔ `Ollama (Local)`

### 3. Governance Interface (ConfigUI)
A **React/Chakra UI** dashboard that allows real-time configuration of:
- API Keys (Stored in a local encrypted vault).
- Personality (SOUL.md).
- Permissions and Fallback Toggles.

### 4. Enterprise Identity Gateway
Authentication is managed by a containerized **Keycloak** instance, supporting identity federation (Google/GitHub) and standard OpenID Connect (OIDC) flows.

## Execution Flow

```mermaid
graph TD
    User(Telegram User) -->|Message| TG[Telegram Gateway]
    TG -->|Process| NC[NeuralCore]
    NC -->|Check Resilience| FC{Strategy Fail?}
    FC -->|Yes (429)| Rot[Rotate Provider]
    FC -->|No| Exec[Execute Skills/Tools]
    Exec -->|Success| Resp[Send Response]
    NC -->|Sync State| Vault[Local KeyVault]
    Admin(Admin) -->|Configure| UI[ConfigUI]
    UI -->|Auth| KC[Keycloak]
    UI -->|Update Settings| NC
```
