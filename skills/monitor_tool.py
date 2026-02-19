import json
import os
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Constants
LOG_DIR_BASE = Path("logs/runs")
PERFORMANCE_LOG = Path(".agent/PERFORMANCE_LOG.toon")
REPORT_SINK = Path(".agent/REPORTS")
PERFORMANCE_REPORT_PATH = REPORT_SINK / "PERFORMANCE_REPORT.md"

def log_event(event: str, status: str, error: str = None):
    """Governance Rule #6: Structured Logging"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_DIR_BASE / date_str
    log_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = f"tool_mon_{int(datetime.now().timestamp())}"
    log_file = log_dir / f"run_{run_id}.jsonl"
    
    log_entry = {
        "ts": datetime.now().isoformat(),
        "run_id": run_id,
        "task_id": "T-MONITOR",
        "agent": "MonitorTool",
        "event": event,
        "status": status,
        "duration_ms": 0,
        "artifacts": [str(PERFORMANCE_REPORT_PATH)] if status == "done" else [],
        "retries": 0,
        "error": error
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def parse_logs():
    all_events = []
    if not LOG_DIR_BASE.exists():
        return []
    
    for date_dir in LOG_DIR_BASE.iterdir():
        if date_dir.is_dir():
            for log_file in date_dir.glob("*.jsonl"):
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            all_events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
    return all_events

def parse_perf_log():
    perf_data = []
    if not PERFORMANCE_LOG.exists():
        return []
    
    with open(PERFORMANCE_LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Skip header and separator
    for line in lines[4:]:
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3:
            perf_data.append({
                "ts": parts[0],
                "operation": parts[1],
                "latency": int(parts[2].replace("ms", ""))
            })
    return perf_data

def generate_report():
    try:
        events = parse_logs()
        perf = parse_perf_log()
        
        # Aggregations
        agent_counts = defaultdict(int)
        agent_status = defaultdict(lambda: defaultdict(int))
        tool_usage = defaultdict(int)
        
        for e in events:
            agent = e.get("agent", "unknown")
            agent_counts[agent] += 1
            agent_status[agent][e.get("status", "unknown")] += 1
            if "tool" in agent.lower():
                tool_usage[agent] += 1
        
        # Report Generation
        report = []
        report.append("# PERFORMANCE REPORT")
        report.append(f"Generated at: {datetime.now().isoformat()}\n")
        
        report.append("## 1. Agent Activity")
        report.append("| Agent | Total Events | Success | Errors |")
        report.append("| :--- | :--- | :--- | :--- |")
        for agent, count in agent_counts.items():
            success = agent_status[agent].get("done", 0) + agent_status[agent].get("concluido", 0)
            errors = agent_status[agent].get("error", 0)
            report.append(f"| {agent} | {count} | {success} | {errors} |")
        
        report.append("\n## 2. Latency Insights (Top 5 Slowest Operations)")
        report.append("| Operation | Timestamp | Latency |")
        report.append("| :--- | :--- | :--- |")
        sorted_perf = sorted(perf, key=lambda x: x["latency"], reverse=True)[:5]
        for p in sorted_perf:
            report.append(f"| {p['operation']} | {p['ts']} | {p['latency']}ms |")
        
        report.append("\n## 3. Tool Usage Patterns")
        if tool_usage:
            for tool, count in tool_usage.items():
                report.append(f"- **{tool}**: used {count} times.")
        else:
            report.append("No specialized tool usage detected.")
            
        report.append("\n## 4. Recommendations")
        avg_latency = sum(p['latency'] for p in perf) / len(perf) if perf else 0
        if avg_latency > 1000:
            report.append("- [!] High average latency detected (>1s). Consider optimizing Database or Search algorithms.")
        if any(agent_status[a].get("error", 0) > 0 for a in agent_counts):
            report.append("- [!] Errors detected in agent execution. Review JSONL logs for root cause analysis.")
        
        if not REPORT_SINK.exists():
            REPORT_SINK.mkdir(parents=True, exist_ok=True)
            
        with open(PERFORMANCE_REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
            
        log_event("generate_report", "done")
        print(f"Performance report generated at {PERFORMANCE_REPORT_PATH}")
        
    except Exception as e:
        log_event("generate_report", "error", error=str(e))
        print(f"Error generating report: {e}")

def main():
    parser = argparse.ArgumentParser(description="Monitoring Tool for Ronaldinho Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Report
    subparsers.add_parser("report", help="Generate performance report")
    
    args = parser.parse_args()
    
    if args.command == "report":
        generate_report()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
