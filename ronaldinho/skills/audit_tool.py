import os
import sys
import json
import time

def audit_logs(audit_dir, log_file):
    """
    Parses JSONL logs and identifies 'ERROR' or 'FAILED' statuses.
    """
    if not os.path.exists(audit_dir):
        return []

    errors = []
    log_path = os.path.join(audit_dir, log_file)
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("status") in ["ERROR", "FAILED", "FALHA"]:
                        errors.append(entry)
                except:
                    continue
    return errors

def update_troubleshooting_log(memory_path, errors):
    if not errors: return
    
    log_file = os.path.join(memory_path, "troubleshooting_log.toon")
    with open(log_file, "a", encoding="utf-8") as f:
        for err in errors:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(err['ts']))
            f.write(f"| {timestamp} | {err['agent']} | {err['event']} | {err.get('mission_id', 'N/A')} |\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: python audit_tool.py [audit_dir] [memory_dir]")
        return

    audit_dir = sys.argv[1]
    memory_dir = sys.argv[2]
    
    today_log = f"run_{time.strftime('%Y%m%d')}.jsonl"
    errors = audit_logs(audit_dir, today_log)
    
    if errors:
        print(f"Detected {len(errors)} errors. Updating memory...")
        update_troubleshooting_log(memory_dir, errors)
    else:
        print("No errors detected in today's logs.")

if __name__ == "__main__":
    main()
