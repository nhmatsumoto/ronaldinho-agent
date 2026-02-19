# Security Model & Governance

Ronaldinho-Agent follows a **Zero-Trust** security philosophy, primarily implemented through the `SecurityGuard` system.

## 1. SecurityGuard (L4 Protection)
The `SecurityGuard` consists of active monitoring and reactive tools to prevent data leaks and unauthorized access.

### Encryption (`security_tool.py`)
- Ronaldinho provides a tool to encrypt sensitive data locally using the **Fernet** symmetric encryption (built on AES).
- **Key Policy**: Encryption keys are generated locally and are **never** stored by the agent. The user must provide the key for any operation involving encrypted data.

### Log Sanitization (`security_scrub_tool.py`)
- Every log entry passes through a regex-based scrubber before being written to disk.
- **PII Protection**: Automatically detects and redacts:
    - Emails
    - Credit Card numbers
    - API keys and Secrets
- This ensures that even if audit logs are shared, sensitive information remains protected.

## 2. Governance Rules
All internal tools follow the **Operational Rules** defined in the project:
- **Rule #4 (Local Autonomy)**: The agent operates strictly within the workspace directory.
- **Rule #6 (Structured Logging)**: Every execution must generate a JSONL trace for auditability.
- **Rule #10 (Determinism)**: Workflows must be reproducible and depend only on local state.

## 3. Security Audit Scripts
The agent can run self-diagnostic scripts to ensure that no credentials have been accidentally committed to the workspace or exposed in un-sanitized reports.
