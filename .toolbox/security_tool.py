import argparse
import os
import json
import base64
from pathlib import Path
from datetime import datetime
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

# Constants
SECRETS_DIR = Path("workspace/data/secrets")
LOG_DIR_BASE = Path("logs/runs")

def log_event(event: str, status: str, error: str = None):
    """Governance Rule #6: Structured Logging"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_DIR_BASE / date_str
    log_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = f"tool_security_{int(datetime.now().timestamp())}"
    log_file = log_dir / f"run_{run_id}.jsonl"
    
    log_entry = {
        "ts": datetime.now().isoformat(),
        "run_id": run_id,
        "task_id": "T-SECURITY",
        "agent": "SecurityTool",
        "event": event,
        "status": status,
        "error": error
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def generate_key():
    """Generates a local key. INSTRUCTION: User should keep this key secure."""
    if Fernet is None:
        print("Error: 'cryptography' library not installed. Cannot generate key.")
        return
    key = Fernet.generate_key()
    print("--------------------------------------------------")
    print("NEW SECURITY KEY GENERATED (LOCAL ONLY)")
    print(key.decode())
    print("--------------------------------------------------")
    print("IMPORTANT: Save this key. Ronaldinho will NOT store it.")
    log_event("generate_key", "done")

def encrypt_data(data, key_str):
    if Fernet is None:
        return "Error: Library missing"
    try:
        f = Fernet(key_str.encode())
        encrypted = f.encrypt(data.encode())
        log_event("encrypt", "done")
        return encrypted.decode()
    except Exception as e:
        log_event("encrypt", "error", error=str(e))
        return f"Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="Zero-Trust Security Tool for Ronaldinho Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    subparsers.add_parser("gen-key", help="Generate a local encryption key")
    
    enc_parser = subparsers.add_parser("encrypt", help="Encrypt a string locally")
    enc_parser.add_argument("--key", required=True, help="Your local private key")
    enc_parser.add_argument("--data", required=True, help="Data to encrypt")
    
    args = parser.parse_args()
    
    if args.command == "gen-key":
        generate_key()
    elif args.command == "encrypt":
        print(encrypt_data(args.data, args.key))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
