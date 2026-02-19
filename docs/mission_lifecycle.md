# Mission Lifecycle

The Ronaldinho-Agent is an mission-oriented ecosystem. Every action the agent takes is defined as a "Mission" within the `ronaldinho/config/mission_store.toon` state file.

## 1. Mission Detection
The Ronaldinho Daemon (`ronaldinho/core/runner.py`) continuously monitors the `mission_store.toon` file. It uses a parser to extract missions and identifies those with the following statuses:
- `EM_PLANEJAMENTO` (Planning)
- `EM_EXECUCAO` (Execution)
- `EM_PROGRESSO` (In Progress)

## 2. Execution Flow
Once a mission is identified, the runner follows this sequence:
1. **Logging**: The Orquestrador logs the mission start in the `ronaldinho/audit/` logs.
2. **Status Update**: The mission status in the `.toon` file is updated to `EM_PROGRESSO`.
3. **Task Handling**: The runner handles the logic associated with the mission (in LITE mode, this is a simulated delay; in full mode, this triggers specialized skills).
4. **Completion**: Upon successful execution, the status is updated to `CONCLUIDO` (Completed).

## 3. Automated Optimization (M-OPT)
During the self-audit loop, Ronaldinho analyzes its own performance logs. If an opportunity for optimization is found (e.g., high latency in a specific skill), it can automatically generate new missions prefixed with `M-OPT-`.

## 4. State Persistence
All state is stored in `.toon` files (Table-Oriented Object Notation). This format ensures that the agent's memory and mission list are human-readable and easy for both the agent and the user to modify.
