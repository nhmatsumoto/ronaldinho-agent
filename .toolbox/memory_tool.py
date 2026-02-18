import json
import os
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Constants
MEMORY_DIR = Path(".agent/knowledge/memory")
COMMIT_DIR = MEMORY_DIR / "commits"
LOG_DIR_BASE = Path("logs/runs")

def log_event(event: str, status: str, artifacts: list = None, error: str = None):
    """Governance Rule #6: Structured Logging"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_DIR_BASE / date_str
    log_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = f"tool_mem_{int(time.time())}"
    log_file = log_dir / f"run_{run_id}.jsonl"
    
    log_entry = {
        "ts": datetime.now().isoformat(),
        "run_id": run_id,
        "task_id": "T-MEMORY",
        "agent": "MemoryTool",
        "event": event,
        "status": status,
        "duration_ms": 0,
        "artifacts": artifacts or [],
        "retries": 0,
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

def commit(summary: str):
    try:
        if not COMMIT_DIR.exists():
            COMMIT_DIR.mkdir(parents=True, exist_ok=True)
            
        timestamp = datetime.now().isoformat()
        commit_id = f"MEM-{int(time.time())}"
        
        # Capture context into a file in the memory repo
        mission_store = read_toon_table(Path(".agent/MISSION_STORE.toon"))
        project_info = read_toon_table(Path(".agent/PROJECT_INFO.toon"))
        
        snapshot = {
            "commit_id": commit_id,
            "timestamp": timestamp,
            "summary": summary,
            "context": {
                "mission_store": mission_store,
                "project_info": project_info
            }
        }
        
        snapshot_path = COMMIT_DIR / f"state.json"
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4)
            
        # Git Lifecycle for Memory Repo
        run_git_command(["add", "."])
        run_git_command(["commit", "-m", f"[{commit_id}] {summary}"])
        
        log_event("commit", "done", artifacts=[str(snapshot_path)])
        print(f"Context committed to memory repository: {commit_id}")
        
    except Exception as e:
        log_event("commit", "error", error=str(e))
        print(f"Error during memory commit: {e}")

def search(query: str):
    try:
        # Use git log to search commit messages
        print(f"Searching memory for: {query}")
        results = run_git_command(["log", "--grep", query, "--oneline"])
        
        if not results.strip():
            print("No matching memory commits found.")
        else:
            print(results)
                
        log_event("search", "done")
    except Exception as e:
        log_event("search", "error", error=str(e))
        print(f"Error during memory search: {e}")

def main():
    parser = argparse.ArgumentParser(description="Git-based Memory Management Tool for Ronaldinho Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Commit
    commit_parser = subparsers.add_parser("commit", help="Commit current context to memory")
    commit_parser.add_argument("--summary", required=True, help="Summary of the context state")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search the memory history")
    search_parser.add_argument("--query", required=True, help="Query string")
    
    args = parser.parse_args()
    
    if args.command == "commit":
        commit(args.summary)
    elif args.command == "search":
        search(args.query)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
