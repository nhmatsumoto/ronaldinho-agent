# Ronaldinho-Agent 🚀 (Open Source Edition)

Ronaldinho-Agent is an autonomous development ecosystem designed for high performance, security, and self-evolution. Built to operate as a background daemon, it manages missions and optimizes your workspace autonomously.

## 🌟 Capabilities

- **L6 Autonomy**: Self-starting, self-correcting, and self-optimizing.
- **Multitasking Core**: Processes multiple missions simultaneously via the Task Parallel Library.
- **Unified Gemini CLI**: A single entry point for all agent operations.
- **Antigravity Ready**: Optimized for the next-generation agentic programming environment.
- **Security-First**: Integrated `SecurityGuard` to protect keys and sanitize logs.

---

## 🧠 How Ronaldinho Works

Ronaldinho is more than just a chatbot; it's a **state-driven orchestration engine**. Here is how it operates:

1.  **State Observation**: The agent constantly watches the `ronaldinho/config/MISSION_STORE.toon` file. Any mission added there becomes a goal for the agent.
2.  **Autonomous Execution**: When a mission is detected, the **Orquestrador** delegates the work to a specialized **Skill** (standardized Python modules).
3.  **Audit & Evolution**: Every action is logged in JSONL format. A background **Self-Audit loop** analyzes these logs to identify errors and performance bottlenecks, which may trigger new optimization missions automatically.
4.  **Zero-Trust Security**: Interaction with sensitive data is gated by the `SecurityGuard`, ensuring that your keys are never stored and your logs are always sanitized.

For a deeper dive into these processes, see our [Internal Documentation](docs/architecture.md).

---

## 🚀 Quick Start

### 1. Credentials Setup

Copy `.env.example` to `.env` and add your Gemini API Key:

```env
GEMINI_API_KEY=your_key_here
```

### 2. Choose Your Environment

#### 🪐 Antigravity (Recommended)

1. Download and install **Antigravity**.
2. Open the `Ronaldinho-Agent` folder.
3. The agent will be automatically detected.

#### 🛠️ Internal Gemini CLI

- **Start the Agent**:
  ```bash
  python gemini_cli.py start
  ```
- **Sync Memory**:
  ```bash
  python gemini_cli.py sync --summary "Brief description of work"
  ```

---

## 🎮 Navigation & Documentation

Learn more about Ronaldinho's internal mechanics:

- 📑 [Mission Lifecycle](docs/mission_lifecycle.md): How tasks are managed.
- 🛡️ [Security & Privacy](docs/security_model.md): How your data is protected.
- 🧬 [Autonomy & Self-Audit](docs/autonomy_audit.md): How the agent evolves.
- 🏗️ [Architecture](docs/architecture.md): The modular system design.

---
*Ronaldinho-Agent: Where autonomy meets engineering mastery.*
