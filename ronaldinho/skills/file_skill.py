import os
import sys

WORKSPACE_DIR = os.path.join(os.getcwd(), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def create_file(filename, content):
    path = os.path.join(WORKSPACE_DIR, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Arquivo '{filename}' criado com sucesso em workspace/."
    except Exception as e:
        return f"Erro ao criar arquivo: {e}"

def read_file(filename):
    path = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(path):
        return f"Arquivo '{filename}' nao encontrado em workspace/."
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"

def list_files(directory="."):
    # Always stay within workspace/
    base_path = os.path.join(WORKSPACE_DIR, directory)
    try:
        files = os.listdir(base_path)
        return "\n".join(files)
    except Exception as e:
        return f"Erro ao listar arquivos: {e}"

def send(filename):
    """Validation for bridge document sending - ensures file exists in workspace/"""
    path = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(path):
        print(f"Error: File '{path}' not found.")
        sys.exit(1)
    print(os.path.abspath(path)) # Bridge expects absolute path on stdout
    return os.path.abspath(path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: file_skill.py [create|read|list|send] [args...]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    if cmd == "create" and len(sys.argv) >= 3:
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        print(create_file(sys.argv[2], content))
    elif cmd == "send" and len(sys.argv) >= 3:
        print(send(sys.argv[2]))
    elif cmd == "read" and len(sys.argv) >= 3:
        print(read_file(sys.argv[2]))
    elif cmd == "list":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        print(list_files(path))
