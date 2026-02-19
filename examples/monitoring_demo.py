import os
import sys
import subprocess
from pathlib import Path

# Paths
WORKSPACE_ROOT = Path(__file__).parents[1]
MONITOR_TOOL = WORKSPACE_ROOT / "ronaldinho" / "skills" / "monitor_tool.py"

def demo_monitoring():
    print("📈 Ronaldinho Monitoring & Performance Demo\n")
    
    # 1. Trigger Report
    print("--- 1. Report Generation Proof ---")
    print("Scenario: Generating a technical performance report from existing logs.")
    
    try:
        # Run the monitor tool
        result = subprocess.run([sys.executable, str(MONITOR_TOOL), "report"], capture_output=True, text=True)
        print(result.stdout)
        
        report_path = WORKSPACE_ROOT / ".agent" / "REPORTS" / "PERFORMANCE_REPORT.md"
        if report_path.exists():
            print(f"✅ SUCCESS: Technical report found at {report_path}")
            print("\nPreview of Report Content (First 10 lines):")
            with open(report_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[:10]:
                    print(f"  {line.strip()}")
            print("...")
        else:
            print("❌ FAILURE: Report was not generated.")
            
    except Exception as e:
        print(f"❌ Error during demo: {e}")

if __name__ == "__main__":
    demo_monitoring()
