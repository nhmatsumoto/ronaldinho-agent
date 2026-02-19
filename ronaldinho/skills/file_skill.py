import os
import sys

def create_file(path, content=""):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Arquivo '{path}' criado com sucesso."
    except Exception as e:
        return f"Erro ao criar arquivo: {e}"

def read_file(path):
    try:
        if not os.path.exists(path):
            return f"Arquivo '{path}' não encontrado."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"

def list_dir(path="."):
    try:
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Erro ao listar diretório: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: file_skill.py [create|read|list] [args...]")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    if cmd == "create" and len(sys.argv) >= 3:
        content = sys.argv[3] if len(sys.argv) > 3 else ""
        print(create_file(sys.argv[2], content))
    elif cmd == "send" and len(sys.argv) >= 3:
        # The runner will handle the actual sending via bridge_tool
        # This skill just validates the file existence and returns the path
        path = sys.argv[2]
        if os.path.exists(path):
            print(os.path.abspath(path))
        else:
            print(f"Erro: Arquivo '{path}' não encontrado.")
    elif cmd == "read" and len(sys.argv) >= 3:
        print(read_file(sys.argv[2]))
    elif cmd == "list":
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        print(list_dir(path))
