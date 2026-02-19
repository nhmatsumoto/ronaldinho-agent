import os
import sys
import json
import subprocess

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKILLS_DIR = os.path.join(WORKSPACE_ROOT, "ronaldinho", "skills")

def explore_and_resolve(instruction):
    """
    Fallback logic: 
    1. Map project
    2. Try to find relevant keywords in file tree
    3. Return a plan to read those files or perform actions
    """
    print(f"🔍 Agentic Research starting for: {instruction}")
    
    # 1. Map project to get current state
    context_script = os.path.join(SKILLS_DIR, "context_skill.py")
    res = subprocess.run(["python", context_script, "map"], capture_output=True, text=True)
    project_map = res.stdout
    
    # 2. Heuristic: If user mentioned "index", find index files
    if "index" in instruction.lower():
        relevant_files = [f for f in project_map.splitlines() if "index" in f.lower()]
        if relevant_files:
            print(f"🎯 Found relevant files: {relevant_files}")
            # Logic would continue to read or edit...
            
    # For now, return a high-intelligence conversation response explaining the research
    return {
        "skill": "gemini", 
        "action": "chat", 
        "args": [f"Pesquisei o campo e já mapeei o projeto. 🏟️\n\nIdentifiquei a estrutura do repositório e estou pronto para operar. Como posso te ajudar com os arquivos listados? ⚽🤖"]
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    instr = sys.argv[1]
    result = explore_and_resolve(instr)
    print(json.dumps(result))
