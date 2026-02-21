# Project Architecture

Ronaldinho-Agent follows a modular, specialist-driven architecture designed for scalability and local autonomy.

## Directory Structure

```text
Ronaldinho-Agent/
├── ronaldinho/            # Core Agent Ecosystem
│   ├── audit/             # JSONL execution logs for auditability
│   ├── config/            # State and configuration (.toon files)
│   ├── core/              # Main runner and orchestration logic
│   ├── memory/            # Long-term knowledge and context snapshots
│   ├── skills/            # Specialized Python tools (Security, Audit, Memory)
├── workspace/             # User data and session runtime
├── docs/                  # Technical documentation and process guides
├── logs/                  # System-level logs
├── start_neural.ps1       # Standard entry point (NeuralCore)
└── README.md              # Project overview and quick start
```

## Key Components

### 1. The NeuralCore (Orchestrator)

The central brain (C#/.NET 9) that manages multi-agent coordination via Semantic Kernel. It orchestrates specialists and ensures governance rules are followed.

### 2. Specialized Skills
Standardized Python modules that the agent can call to perform specific technical tasks:

- **SecurityTool**: Handles encryption and scrubbing.
- **MonitorTool**: Analyzes performance.
- **MemoryTool**: Manage context and sync.

### 3. The TOON Layer
All configuration and state management use **Table-Oriented Object Notation**. This makes the project's internal state highly digestible for LLMs while remaining 100% human-editable in basic text editors.

## Execution Flow

```mermaid
graph TD
    User(User) -->|Creates Mission| MS[mission_store.toon]
    MS -->|Polled by| Runner[Core Runner]
    Runner -->|Delegates to| Skill[Specialized Skill]
    Skill -->|Logs Trace| Audit[Audit Logs]
    Audit -->|Analyzed by| SelfAudit[Self-Audit Loop]
    SelfAudit -->|Updates| Memory[Troubleshooting Log]
```
