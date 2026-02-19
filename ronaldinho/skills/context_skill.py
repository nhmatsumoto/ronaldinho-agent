import os
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
MISSION_STORE = WORKSPACE_ROOT / "ronaldinho" / "config" / "mission_store.toon"
AUDIT_DIR = WORKSPACE_ROOT / "ronaldinho" / "audit"

def get_missions():
    if not MISSION_STORE.exists():
        return "Nenhuma missão encontrada."
    try:
        with open(MISSION_STORE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler missões: {e}"

def get_audit_summary():
    if not AUDIT_DIR.exists():
        return "Nenhum log de auditoria encontrado."
    try:
        logs = sorted(AUDIT_DIR.glob("*.jsonl"))
        if not logs:
            return "Nenhum log encontrado."
        # Read the last 10 lines of the most recent log
        with open(logs[-1], "r", encoding="utf-8") as f:
            lines = f.readlines()
            return "".join(lines[-10:])
    except Exception as e:
        return f"Erro ao ler logs: {e}"

def list_project_structure():
    try:
        output = []
        for root, dirs, files in os.walk(WORKSPACE_ROOT):
            # Ignore hidden dirs and build artifacts
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["bin", "obj", "__pycache__"]]
            level = root.replace(str(WORKSPACE_ROOT), "").count(os.sep)
            indent = " " * 4 * level
            output.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for f in files:
                if not f.startswith("."):
                    output.append(f"{sub_indent}{f}")
        return "\n".join(output[:50]) # Limit to 50 items for context
    except Exception as e:
        return f"Erro ao listar estrutura: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: context_skill.py [missions|audit|structure]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "missions":
        print(get_missions())
    elif cmd == "audit":
        print(get_audit_summary())
    elif cmd == "structure":
        print(list_project_structure())
