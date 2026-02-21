# Ronaldinho Remote Control (Telegram Setup)

This guide explains how to set up the Telegram Bridge to interact with Ronaldinho remotely while maintaining **Local-Only Governance**.

## 1. Prerequisites

- **.NET 9 SDK** (already verified on your machine).
- Your Telegram Bot Token (already saved in `workspace/data/secrets/telegram.json`).

## 2. Start Ronaldinho (Unified Command)

The easiest way to start everything is with a single command:

```powershell
.\dev_scripts\start_ronaldinho.ps1
```

This will automatically:

- Start the **NeuralCore (Brain)** (.NET) in a new window.
- Start the **Telegram Bridge** (.NET) in a separate background process.

## 3. Manual Startup (Optional)

If you need to run the bridge service independently for debugging, you can still run it manually:

```bash
dotnet run --project services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj
```

## 4. Interaction Flow

- **You** send a message to `@ronaldinho_agent_bot` on Telegram.
- **Ronaldinho.Bridge** (.NET) polls Telegram and writes your message to `workspace/data/telegram/inbox.jsonl`.
- **Ronaldinho Agent** (Python) monitors the inbox, processes the request, and writes a response to `outbox.jsonl`.
- **Ronaldinho.Bridge** (.NET) detects the response and sends it back to you on Telegram.

> [!TIP]
> This new .NET service is much more resilient than the previous script, thanks to Hangfire's automatic retries and SQLite-backed job storage.
