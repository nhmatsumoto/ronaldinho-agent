import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(__file__).parents[1]
AUDIT_DIR = WORKSPACE_ROOT / "ronaldinho" / "audit"
MEMORY_DIR = WORKSPACE_ROOT / "ronaldinho" / "memory"
AUDIT_TOOL = WORKSPACE_ROOT / "ronaldinho" / "skills" / "audit_tool.py"
MISSION_STORE = WORKSPACE_ROOT / "ronaldinho" / "config" / "mission_store.toon"

def demo_autonomy():
    print("🧬 Ronaldinho Autonomy & Audit Demo\n")
    
    # 1. Simulate a real mission cycle (Simplified)
    print("--- 1. Mission Completion Proof ---")
    mission_id = "M-DEMO-001"
    print(f"Scenario: Simulating the completion of mission {mission_id}.")
    
    # Inject a success log entry
    log_file = AUDIT_DIR / f"run_{time.strftime('%Y%m%d')}.jsonl"
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "ts": time.time(),
        "agent": "Orquestrador",
        "event": "Finalizando missão Demo",
        "status": "SUCESSO",
        "mission_id": mission_id
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"✅ Mission {mission_id} success entry added to logs.")

    # 2. Simulate failure and self-correction
    print("\n--- 2. Self-Correction (Audit) Proof ---")
    fail_id = "M-DEMO-FAIL"
    print(f"Scenario: Injecting a failure for {fail_id} and triggering the Audit loop.")
    
    fail_entry = {
        "ts": time.time(),
        "agent": "Specialist",
        "event": "Data Processing",
        "status": "FAILED",
        "mission_id": fail_id
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(fail_entry) + "\n")
    
    # Trigger Audit Tool
    print("Running Audit Loop...")
    subprocess.run([sys.executable, str(AUDIT_TOOL), str(AUDIT_DIR), str(MEMORY_DIR)], check=True)
    
    trouble_log = MEMORY_DIR / "troubleshooting_log.toon"
    print(f"Checking for entry in {trouble_log.name}...")
    
    with open(trouble_log, "r", encoding="utf-8") as f:
        content = f.read()
        if fail_id in content:
            print(f"✅ SUCCESS: The agent identified the failure in {fail_id} and moved it to its internal memory.")
        else:
            print("❌ FAILURE: Audit loop did not capture the error.")

if __name__ == "__main__":
    demo_autonomy()
