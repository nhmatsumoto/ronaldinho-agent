import json
import argparse
from pathlib import Path
from datetime import datetime

# Path Configuration
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INBOX_FILE = BASE_DIR / "workspace/data/telegram/inbox.jsonl"
OUTBOX_FILE = BASE_DIR / "workspace/data/telegram/outbox.jsonl"

def read_new_messages():
    """Reads messages from inbox that haven't been processed yet."""
    if not INBOX_FILE.exists():
        return []

    new_messages = []
    updated_lines = []
    
    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if not data.get("processed"):
                    new_messages.append(data)
                    data["processed"] = True
                    data["processed_at"] = datetime.now().isoformat()
                updated_lines.append(json.dumps(data) + "\n")
            except:
                continue

    # Update inbox file with 'processed' flags
    with open(INBOX_FILE, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)
    
    return new_messages

def send_response(user_id, text):
    """Writes a response to the outbox for the bridge to pick up."""
    entry = {
        "ts": datetime.now().isoformat(),
        "user_id": user_id,
        "text": text,
        "sent": False
    }
    OUTBOX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTBOX_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[+] Response for {user_id} added to outbox.")

def main():
    parser = argparse.ArgumentParser(description="Ronaldinho Internal Bridge Tool")
    parser.add_argument("--check", action="store_true", help="Check for and print new messages")
    parser.add_argument("--respond", nargs=2, metavar=('USER_ID', 'TEXT'), help="Send a response to a user")
    
    args = parser.parse_args()

    if args.check:
        messages = read_new_messages()
        if messages:
            print(json.dumps(messages, indent=2))
        else:
            print("[]")
    
    elif args.respond:
        send_response(args.respond[0], args.respond[1])
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
