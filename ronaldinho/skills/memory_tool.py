import json
import os
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Updated Constants for Themed Structure
WORKSPACE_ROOT = Path(__file__).parents[2]
MEMORY_DIR = WORKSPACE_ROOT / "ronaldinho" / "memory"
CONFIG_DIR = WORKSPACE_ROOT / "ronaldinho" / "config"
LOG_DIR_BASE = WORKSPACE_ROOT / "ronaldinho" / "audit"

def log_event(event: str, status: str, artifacts: list = None, error: str = None):
    """Governance Rule #6: Structured Logging"""
    log_dir = LOG_DIR_BASE
    log_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"memory_sync_{date_str}.jsonl"
    
    log_entry = {
        "ts": time.time(),
        "agent": "MemoryTool",
        "event": event,
        "status": status,
        "artifacts": artifacts or [],
        "error": error
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def run_git_command(args, cwd=MEMORY_DIR):
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git error: {result.stderr}")
    return result.stdout

def read_toon_table(path: Path) -> str:
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def sync(summary: str):
    try:
        if not MEMORY_DIR.exists():
            MEMORY_DIR.mkdir(parents=True, exist_ok=True)
            
        # Initialize if not a repo
        if not (MEMORY_DIR / ".git").exists():
            print("Initializing memory repository...")
            run_git_command(["init"])
            
        timestamp = datetime.now().isoformat()
        commit_id = f"MEM-{int(time.time())}"
        
        # Capture context into the memory repo
        mission_store = read_toon_table(CONFIG_DIR / "MISSION_STORE.toon")
        project_info = read_toon_table(CONFIG_DIR / "PROJECT_INFO.toon")
        
        snapshot = {
            "commit_id": commit_id,
            "timestamp": timestamp,
            "summary": summary,
            "context": {
                "mission_store": mission_store,
                "project_info": project_info
            }
        }
        
        snapshot_dir = MEMORY_DIR / "snapshots"
        snapshot_dir.mkdir(exist_ok=True)
        snapshot_path = snapshot_dir / "latest_context.json"
        
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4)
            
        # Git Lifecycle
        run_git_command(["add", "."])
        # Check if there are changes to commit
        status = run_git_command(["status", "--porcelain"])
        if status.strip():
            run_git_command(["commit", "-m", f"[{commit_id}] {summary}"])
            print(f"Context committed: {commit_id}")
            
            # Push to GitHub
            try:
                print("Syncing with GitHub...")
                run_git_command(["push", "origin", "master"]) # Assuming master/main
                log_event("sync", "SUCCESS", artifacts=[str(snapshot_path)])
            except Exception as push_err:
                print(f"Warning: Could not push to remote. Is 'origin' configured? {push_err}")
                log_event("sync", "COMMIT_ONLY", error=str(push_err))
        else:
            print("No changes to sync.")
        
    except Exception as e:
        log_event("sync", "ERROR", error=str(e))
        print(f"Error during memory sync: {e}")

def main():
    parser = argparse.ArgumentParser(description="GitHub-integrated Memory Tool for Ronaldinho Agent")
    parser.add_argument("command", choices=["sync"], help="Commands")
    parser.add_argument("--summary", required=True, help="Summary of the context state")
    
    args = parser.parse_args()
    
    if args.command == "sync":
        sync(args.summary)

if __name__ == "__main__":
    main()
