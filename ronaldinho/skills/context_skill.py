import os
import sys
import json
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent

def map_project(max_depth=3):
    """Generates a recursive map of the project structure."""
    tree = []
    ignore = {".git", "__pycache__", "bin", "obj", "node_modules", ".venv"}
    
    def walk(path, depth):
        if depth > max_depth: return
        try:
            for item in sorted(os.listdir(path)):
                if item in ignore: continue
                full_path = os.path.join(path, item)
                rel_path = os.path.relpath(full_path, WORKSPACE_ROOT)
                is_dir = os.path.isdir(full_path)
                
                prefix = "  " * depth + ("📁 " if is_dir else "📄 ")
                tree.append(f"{prefix}{rel_path}")
                
                if is_dir:
                    walk(full_path, depth + 1)
        except Exception as e:
            tree.append(f"  " * depth + f"⚠️ Error reading {path}: {e}")

    walk(WORKSPACE_ROOT, 0)
    result = "\n".join(tree)
    print(result)
    return result

def get_summary():
    """Returns a high-level summary of the project state."""
    summary = []
    summary.append(f"Projeto: Ronaldinho-Agent")
    summary.append(f"Base: {WORKSPACE_ROOT}")
    
    # Check for missions
    mission_store = WORKSPACE_ROOT / "ronaldinho" / "config" / "mission_store.toon"
    if mission_store.exists():
        with open(mission_store, "r", encoding="utf-8") as f:
            active_missions = [l for l in f.readlines() if "EM_EXECUCAO" in l or "EM_PROGRESSO" in l]
            summary.append(f"Missões Ativas: {len(active_missions)}")
    
    # Check for skills
    skills_dir = WORKSPACE_ROOT / "ronaldinho" / "skills"
    if skills_dir.exists():
        skills = [f for f in os.listdir(skills_dir) if f.endswith(".py")]
        summary.append(f"Habilidades: {len(skills)}")
    
    result = "\n".join(summary)
    print(result)
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: context_skill [map|summary]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "map":
        map_project()
    elif cmd == "summary":
        get_summary()
    else:
        print(f"Comando desconhecido: {cmd}")
