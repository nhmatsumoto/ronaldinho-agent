# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-02-22

This is the first stable release of the modern Ronaldinho-Agent, transitioning from the legacy Python prototype to a robust .NET 9 / React ecosystem.

### Added
- **NeuralCore (.NET 9)**: High-performance orchestration engine using Semantic Kernel.
- **Multi-Model Gateway**: Concurrent support for Gemini 2.0, OpenAI (GPT-4o), and Claude (Anthropic).
- **Zero-Block Resilience**: Automatic provider rotation logic on 429 (Rate Limit) errors.
- **Governance UI (React/Chakra)**: Modern interface for managing API keys, SOUL.md, and system state.
- **Keycloak Integration**: Enterprise-grade OIDC authentication with a dedicated `ronaldinho` realm.
- **Smart Onboarding**: Startup scripts that automatically launch the configuration UI for new users.
- **Security Hardening**: Sanitized Docker configurations and formal `SECURITY.md`.
- **Bilingual Documentation**: Support for both English and Portuguese (PT-BR).

### Changed
- Refactored orchestrator from `gemini_cli.py` (Python) to `Ronaldinho.NeuralCore` (C#).
- Modernized project architecture to a hyper-converged, service-oriented structure.
- Professionalized Git history and repository standardization.

## [0.0.1] - 2026-02-15
- Initial "v1" legacy prototype with basic Python scripts.
- Proof of concept for Telegram-to-Gemini bridge.
