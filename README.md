# Ronaldinho-Agent 🚀 (Open Source Edition)

Ronaldinho-Agent is an autonomous development ecosystem designed for high performance, security, and self-evolution. Built to operate as a background daemon, it manages missions and optimizes your workspace autonomously.

## 🌟 Capabilities

- **L6 Autonomy**: Self-starting, self-correcting, and self-optimizing.
- **Multitasking Core**: Processes multiple missions simultaneously via the Task Parallel Library.
- **Unified Gemini CLI**: A single entry point for all agent operations.
- **Antigravity Ready**: Optimized for the next-generation agentic programming environment.
- **Security-First**: Integrated `SecurityGuard` to protect keys and sanitize logs.

---

## 🚀 Quick Start

### 1. Credentials Setup

Copy `.env.example` to `.env` and add your Gemini API Key:

```env
GEMINI_API_KEY=your_key_here
```

### 2. Choose Your Environment

#### 🪐 Antigravity (Recommended)

Antigravity is the native home for Ronaldinho-Agent.

1. Download and install **Antigravity**.
2. Open the `Ronaldinho-Agent` folder.
3. The agent will be automatically detected and ready for missions.

#### 💻 Visual Studio Code

1. Open the project in VS Code.
2. Ensure you have Python 3.9+ installed.
3. Use the **Gemini CLI** (details below) to start the agent.

#### 🛠️ Internal Gemini CLI

Ronaldinho-Agent comes with a unified control tool: `gemini_cli.py`.

- **Start the Agent**:

  ```bash
  python gemini_cli.py start
  ```

- **Sync Memory/Context**:

  ```bash
  python gemini_cli.py sync --summary "Brief description of work done"
  ```

---

## 🎮 Mission Management

The agent is driven by **Missions**. You interact with it by editing the state files in `ronaldinho/config/`.

1. **Add Missions**: Open `ronaldinho/config/MISSION_STORE.toon` and add your task.
   - Format: `| ID | Title | Status | Priority | Description |`
   - Example: `| M-001 | Optimize DB Queries | EM_PLANEJAMENTO | HIGH | Analysis of slow queries... |`

2. **Monitor Evolution**: Watch the `MISSION_STORE`. Ronaldinho will create `M-OPT-` missions when it identifies opportunities for self-optimization.

3. **Audit Logs**: Check `ronaldinho/audit/` for detailed run history.

---

## 📜 Governance & Rules

Ronaldinho-Agent follows a strict governance model defined in `ronaldinho/config/SECURITY_POLICY.toon`. All actions are logged and audited to ensure safety and determinism.

---
*Ronaldinho-Agent: Where autonomy meets engineering mastery.*
