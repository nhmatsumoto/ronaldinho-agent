import re
import os
import sys

def parse_instruction(text):
    text = text.lower()
    
    # Pattern: Create file
    # Example: "crie um arquivo chamado 'test.txt' com 'hello'"
    create_match = re.search(r"crie (?:um )?arquivo chamado ['\"](.+?)['\"](?: com (?:o texto )?['\"](.+?)['\"])?", text)
    if create_match:
        filename = create_match.group(1)
        content = create_match.group(2) if create_match.group(2) else ""
        return {
            "skill": "file_skill",
            "action": "create",
            "args": [filename, content]
        }
    
    # Pattern: Currency / Dollar (Search simulation)
    if any(k in text for k in ["dolar", "valor do", "cotacao", "pesquise"]):
        return {
            "skill": "orchestrator_skill",
            "action": "create",
            "args": [
                "currency_tool",
                "import random; print(f'Cotacao simulada: R$ {random.uniform(5.5, 5.9):.2f}')"
            ]
        }
    
    # Pattern: List files
    if any(k in text for k in ["liste", "listar", "quais arquivos"]):
        return {
            "skill": "file_skill",
            "action": "list",
            "args": ["."]
        }
        
    return None

if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No instruction provided"}))
        sys.exit(0)
    
    instruction = sys.argv[1]
    result = parse_instruction(instruction)
    if result:
        print(json.dumps(result))
    else:
        print(json.dumps({"error": "Instruction not understood"}))
