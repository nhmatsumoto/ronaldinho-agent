# Security Policy

## Supported Versions

The following versions of Ronaldinho-Agent are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take the security of Ronaldinho-Agent seriously. If you believe you have found a security vulnerability, please report it to us by following these steps:

1. **Do not open a public issue.**
2. Send an email to **security@ronaldinho-agent.local** (placeholder - update with real contact).
3. Include as much detail as possible, including steps to reproduce the issue.

### Our Response Process

- We will acknowledge receipt of your report within 48 hours.
- We will provide an estimated timeline for a fix.
- We will notify you once the vulnerability is addressed.

## General Security Best Practices

- **Never commit your `.env` file.** It contains your API keys and secrets.
- **Rotate your keys regularly.** If you suspect a leak, change your Gemini/OpenAI/Telegram tokens immediately.
- **Use Strong Passwords.** Change the default Keycloak/DB passwords in production via the `.env` file.
- **Local Autonomy.** Ronaldinho is designed to run locally. Be cautious when exposing the Governance UI or NeuralCore API to the internet.
