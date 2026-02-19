import os
import time
import json
import subprocess
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(__file__).parents[1]
AUDIT_DIR = WORKSPACE_ROOT / "ronaldinho" / "audit"
MEMORY_DIR = WORKSPACE_ROOT / "ronaldinho" / "memory"
MISSION_STORE = WORKSPACE_ROOT / "ronaldinho" / "config" / "mission_store.toon"
AUDIT_TOOL = WORKSPACE_ROOT / "ronaldinho" / "skills" / "audit_tool.py"
MONITOR_TOOL = WORKSPACE_ROOT / "ronaldinho" / "skills" / "monitor_tool.py"

def simulate_failure():
    print("🛠️  Simulating a Failed Mission...")
    log_file = AUDIT_DIR / f"run_{time.strftime('%Y%m%d')}.jsonl"
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "ts": time.time(),
        "agent": "TestAgent",
        "event": "Critical Operation",
        "status": "FAILED",
        "mission_id": "M-TEST-999"
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print("✅ Failure injected into audit logs.")

def validate_self_correcting():
    print("\n🔍 Validating Self-Correcting (Audit Loop)...")
    subprocess.run(["python", str(AUDIT_TOOL), str(AUDIT_DIR), str(MEMORY_DIR)], check=True)
    
    trouble_log = MEMORY_DIR / "troubleshooting_log.toon"
    if trouble_log.exists():
        with open(trouble_log, "r", encoding="utf-8") as f:
            content = f.read()
            if "M-TEST-999" in content:
                print("✅ SUCCESS: Failure detected and moved to the Troubleshooting Log.")
                return True
    print("❌ FAILURE: Troubleshooting Log did not capture the simulated error.")
    return False

def validate_self_optimizing():
    print("\n📈 Validating Self-Optimizing (Monitoring)...")
    subprocess.run(["python", str(MONITOR_TOOL), "report"], check=True)
    
    report_path = WORKSPACE_ROOT / ".agent" / "REPORTS" / "PERFORMANCE_REPORT.md"
    if report_path.exists():
        print(f"✅ SUCCESS: Performance report generated at {report_path}")
        return True
    print("❌ FAILURE: Performance report not found.")
    return False

def main():
    print("=== Ronaldinho L6 Autonomy Validation ===\n")
    
    # 1. Self-Starting: Validated by checking if core files exist
    print("🏃 Validating Self-Starting Foundation...")
    if (WORKSPACE_ROOT / "gemini_cli.py").exists() and (WORKSPACE_ROOT / "ronaldinho" / "core" / "runner.py").exists():
        print("✅ SUCCESS: Core runner and CLI ready.")
    else:
        print("❌ FAILURE: Missing core runner components.")

    # 2. Self-Correcting
    simulate_failure()
    sc = validate_self_correcting()

    # 3. Self-Optimizing
    so = validate_self_optimizing()

    print("\n" + "="*40)
    if sc and so:
        print("🏁 FINAL VERDICT: L6 AUTONOMY VALIDATED")
    else:
        print("🏁 FINAL VERDICT: PARTIAL VALIDATION")
    print("="*40)

if __name__ == "__main__":
    main()
