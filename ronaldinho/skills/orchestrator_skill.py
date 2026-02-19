import os
import sys

# Ensure .toolbox exists
TOOLBOX_DIR = os.path.join(os.getcwd(), ".toolbox")
os.makedirs(TOOLBOX_DIR, exist_ok=True)

def create_tool(name, content):
    path = os.path.join(TOOLBOX_DIR, f"{name}.py")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Ferramenta '{name}' criada com sucesso em .toolbox/."
    except Exception as e:
        return f"Erro ao criar ferramenta: {e}"

def run_tool(name, *args):
    path = os.path.join(TOOLBOX_DIR, f"{name}.py")
    if not os.path.exists(path):
        return f"Ferramenta '{name}' nao encontrada."
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, path] + list(args), capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Erro ao executar ferramenta: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: orchestrator_skill.py [create|run] [args...]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "create" and len(sys.argv) >= 4:
        # Args: script_name, content
        print(create_tool(sys.argv[2], sys.argv[3]))
    elif cmd == "run" and len(sys.argv) >= 3:
        # Args: script_name, *tool_args
        print(run_tool(sys.argv[2], *sys.argv[3:]))
