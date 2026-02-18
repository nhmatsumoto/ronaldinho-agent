import json
import os
import time
import argparse
from datetime import datetime
from pathlib import Path

# Constants
COMMIT_DIR = Path(".agent/knowledge/memory/commits")
INDEX_PATH = Path(".agent/knowledge/memory/index.toon")
LOG_DIR_BASE = Path("logs/runs")

def log_event(event: str, status: str, artifacts: list = None, error: str = None):
    """Governance Rule #6: Structured Logging"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_DIR_BASE / date_str
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Simple run_id based on timestamp for the tool itself
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
        
        # Capture context
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
        
        snapshot_path = COMMIT_DIR / f"{commit_id}.json"
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4)
            
        # Update Index
        index_entry = f"| {commit_id} | {timestamp} | Snapshot | {summary[:30]} | {snapshot_path.as_posix()} |\n"
        with open(INDEX_PATH, "a", encoding="utf-8") as f:
            f.write(index_entry)
            
        log_event("commit", "done", artifacts=[str(snapshot_path), str(INDEX_PATH)])
        print(f"Commit {commit_id} created successfully.")
        
    except Exception as e:
        log_event("commit", "error", error=str(e))
        print(f"Error during commit: {e}")

def search(query: str):
    try:
        if not INDEX_PATH.exists():
            print("No index found.")
            return
            
        print(f"Searching for: {query}")
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        results = [line for line in lines if query.lower() in line.lower()]
        if not results:
            print("No results found.")
        else:
            for res in results:
                print(res.strip())
                
        log_event("search", "done")
    except Exception as e:
        log_event("search", "error", error=str(e))
        print(f"Error during search: {e}")

def main():
    parser = argparse.ArgumentParser(description="Memory Management Tool for Ronaldinho Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Commit
    commit_parser = subparsers.add_parser("commit", help="Create a context snapshot")
    commit_parser.add_argument("--summary", required=True, help="Summary of the context state")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search the memory index")
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
