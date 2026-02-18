import json
import argparse
import os
from pathlib import Path
from datetime import datetime

# Constants
SECRETS_DIR = Path("workspace/data/secrets")
LOG_DIR_BASE = Path("logs/runs")

def log_event(event: str, status: str, platform: str = None, error: str = None):
    """Governance Rule #6: Structured Logging"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_DIR_BASE / date_str
    log_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = f"tool_comm_{int(datetime.now().timestamp())}"
    log_file = log_dir / f"run_{run_id}.jsonl"
    
    log_entry = {
        "ts": datetime.now().isoformat(),
        "run_id": run_id,
        "task_id": "T-COMM",
        "agent": "CommunicatorTool",
        "event": event,
        "status": status,
        "platform": platform,
        "error": error
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def send_message(platform, message):
    try:
        secret_path = SECRETS_DIR / f"{platform}.json"
        if not secret_path.exists():
            raise FileNotFoundError(f"Secrets for {platform} not found in {SECRETS_DIR}")
        
        with open(secret_path, "r") as f:
            secrets = json.load(f)
            
        print(f"[Simulated] Sending to {platform}: {message}")
        log_event("send_message", "done", platform=platform)
        
    except Exception as e:
        log_event("send_message", "error", platform=platform, error=str(e))
        print(f"Error sending message to {platform}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Multiplatform Communication Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    send_parser = subparsers.add_parser("send", help="Send a message")
    send_parser.add_argument("--platform", required=True, choices=["slack", "telegram", "whatsapp", "google"], help="Target platform")
    send_parser.add_argument("--message", required=True, help="Message content")
    
    args = parser.parse_args()
    
    if args.command == "send":
        send_message(args.platform, args.message)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
