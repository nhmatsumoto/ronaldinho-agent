import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Configure Paths
BASE_DIR = Path(__file__).resolve().parent.parent
INBOX_FILE = BASE_DIR / "workspace/data/telegram/inbox.jsonl"
OUTBOX_FILE = BASE_DIR / "workspace/data/telegram/outbox.jsonl"
SECRETS_FILE = BASE_DIR / "workspace/data/secrets/telegram.json"

def log_bridge_event(event, status, error=None):
    """Bridge-specific logging"""
    log_file = BASE_DIR / f"logs/runs/{datetime.now().strftime('%Y-%m-%d')}/bridge.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "ts": datetime.now().isoformat(),
        "event": event,
        "status": status,
        "error": error
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def ensure_structure():
    INBOX_FILE.parent.mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "workspace/data/secrets").mkdir(parents=True, exist_ok=True)

class TelegramBridge:
    def __init__(self, token=None):
        self.token = token
        self.last_update_id = 0
        ensure_structure()

    def get_token_from_file(self):
        if SECRETS_FILE.exists():
            with open(SECRETS_FILE, "r") as f:
                data = json.load(f)
                return data.get("token")
        return None

    def poll_telegram(self):
        """Polls Telegram for new messages."""
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code == 200:
                updates = response.json().get("result", [])
                for update in updates:
                    self.last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        user_id = update["message"]["from"]["id"]
                        text = update["message"]["text"]
                        print(f"[!] New message from {user_id}: {text}")
                        self.write_to_inbox(user_id, text)
        except Exception as e:
            print(f"[X] Telegram Poll Error: {e}")
            log_bridge_event("poll_error", "error", error=str(e))

    def write_to_inbox(self, user_id, text):
        entry = {
            "ts": datetime.now().isoformat(),
            "user_id": user_id,
            "text": text,
            "processed": False
        }
        with open(INBOX_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[+] Message added to inbox: {INBOX_FILE.name}")
        log_bridge_event("inbox_write", "done")

    def check_outbox(self):
        if not OUTBOX_FILE.exists():
            return

        with open(OUTBOX_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return

        remaining_lines = []
        for line in lines:
            try:
                import requests
                data = json.loads(line)
                if not data.get("sent"):
                    print(f"[*] Sending response to Telegram (User {data.get('user_id')})...")
                    url = f"https://api.telegram.org/bot{self.token}/sendMessage"
                    payload = {
                        "chat_id": data.get("user_id"),
                        "text": data.get("text")
                    }
                    res = requests.post(url, json=payload, timeout=10)
                    if res.status_code == 200:
                        data["sent"] = True
                        data["sent_at"] = datetime.now().isoformat()
                        log_bridge_event("outbox_send", "done")
                    else:
                        print(f"[X] Failed to send message: {res.text}")
                remaining_lines.append(json.dumps(data) + "\n")
            except Exception as e:
                print(f"[X] Outbox processing error: {e}")
                remaining_lines.append(line)

        # Update outbox to mark as sent
        with open(OUTBOX_FILE, "w", encoding="utf-8") as f:
            f.writelines(remaining_lines)

def main():
    parser = argparse.ArgumentParser(description="Ronaldinho Telegram Bridge")
    parser.add_argument("--token", help="Telegram Bot Token")
    parser.add_argument("--dry-run", action="store_true", help="Test file structure and simulation")
    args = parser.parse_args()

    bridge = TelegramBridge(token=args.token)
    
    if args.dry_run:
        print("[!] Dry Run: Simulating message flow.")
        bridge.write_to_inbox("User123", "Ronaldinho, status report.")
        bridge.check_outbox()
        return

    if not bridge.token:
        bridge.token = bridge.get_token_from_file()

    if not bridge.token:
        print("[!] Error: No token provided. Use --token or place it in workspace/data/secrets/telegram.json")
        return

    print(f"[*] Bridge Started. Monitoring {INBOX_FILE.name} and {OUTBOX_FILE.name}")
    try:
        while True:
            # Poll Telegram -> Write Inbox
            bridge.poll_telegram()
            # Check Outbox -> Send Telegram
            bridge.check_outbox()
            time.sleep(5)
    except KeyboardInterrupt:
        print("[*] Bridge Stopped.")

if __name__ == "__main__":
    main()
