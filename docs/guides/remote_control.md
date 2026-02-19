# Ronaldinho Remote Control (Telegram Setup)

This guide explains how to set up the Telegram Bridge to interact with Ronaldinho remotely while maintaining **Local-Only Governance**.

## 1. Create a Telegram Bot
1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the instructions to get your **Bot Token**.
3. (Optional) Save the token in `workspace/data/secrets/telegram.json`:
   ```json
   {
     "token": "YOUR_BOT_TOKEN_HERE"
   }
   ```

## 2. Run the Bridge Script
On your machine (where the project is located), open a terminal and run:

```bash
python dev_scripts/telegram_bridge.py --token YOUR_BOT_TOKEN_HERE
```

This script will start polling Telegram and exchanging messages with Ronaldinho via local files in `workspace/data/telegram/`.

## 3. Interaction Flow
- **You** send a message to the bot on Telegram.
- **The Bridge** (running locally) writes your message to `inbox.jsonl`.
- **Ronaldinho** (the agent) monitors `inbox.jsonl`, processes the request, and writes a response to `outbox.jsonl`.
- **The Bridge** reads the response from `outbox.jsonl` and sends it back to your Telegram chat.

> [!NOTE]
> Since Ronaldinho follows strict local-only governance, he cannot talk to Telegram directly. The bridge script you run is the "messenger" that makes this possible without compromising security.
