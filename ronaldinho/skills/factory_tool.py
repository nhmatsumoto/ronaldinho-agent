import argparse
import os
import json
from pathlib import Path
from datetime import datetime

# Constants
SPECIALISTS_DIR = Path(".agent/specialists")
LOG_DIR_BASE = Path("logs/runs")
FORBIDDEN_KEYWORDS = ["health", "medicine", "doctor", "diagnosis", "prescription", "hospital", "saúde", "médico"]

def log_event(event: str, status: str, agent_name: str = None, error: str = None):
    """Governance Rule #6: Structured Logging"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = LOG_DIR_BASE / date_str
    log_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = f"tool_factory_{int(datetime.now().timestamp())}"
    log_file = log_dir / f"run_{run_id}.jsonl"
    
    log_entry = {
        "ts": datetime.now().isoformat(),
        "run_id": run_id,
        "task_id": "T-FACTORY",
        "agent": "FactoryTool",
        "event": event,
        "status": status,
        "created_agent": agent_name,
        "error": error
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def check_guardrails(domain_desc):
    """Check if the requested domain violates health/medical restrictions."""
    desc_lower = domain_desc.lower()
    for word in FORBIDDEN_KEYWORDS:
        if word in desc_lower:
            return False, f"Violation: Keyword '{word}' found in domain description. Health-related agents are strictly forbidden."
    return True, "Safe"

def create_specialist(name, domain, specialization):
    try:
        # 1. Guardrail Check
        is_safe, message = check_guardrails(domain + " " + specialization)
        if not is_safe:
            log_event("create_agent", "blocked", agent_name=name, error=message)
            print(f"ERROR: {message}")
            return
        
        # 2. Template Generation
        toon_content = f"""# {name.upper()} AGENT (TOON)

## 🎯 SPECIALIZATION ({domain})
{specialization}

## 🏆 OBJECTIVE
- Definir objetivos específicos para {name}.
- Garantir a entrega de valor no domínio de {domain}.

## 🚧 OBSTACLES (Constraints)
- Limitações técnicas e de negócio.
- Conformidade com a SECURITY_POLICY.toon.

## 👣 WORKFLOW
1. Input Analysis.
2. Processing.
3. Output Validation.

## 🛠️ TOOLKIT
- Ferramentas específicas para {domain}.
"""
        
        file_path = SPECIALISTS_DIR / f"{name.lower()}.toon"
        if file_path.exists():
            print(f"Agent {name} already exists. Skipping.")
            return

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(toon_content)
            
        log_event("create_agent", "done", agent_name=name)
        print(f"Agent {name} created successfully at {file_path}")
        
    except Exception as e:
        log_event("create_agent", "error", agent_name=name, error=str(e))
        print(f"Error creating agent: {e}")

def main():
    parser = argparse.ArgumentParser(description="Specialist Factory Tool for Ronaldinho Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    create_parser = subparsers.add_parser("create", help="Create a new specialist")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument("--domain", required=True, help="Domain (e.g. Finance, Dev)")
    create_parser.add_argument("--spec", required=True, help="Description of specialization")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_specialist(args.name, args.domain, args.spec)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
