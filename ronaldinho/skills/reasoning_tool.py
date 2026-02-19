import re
import os
import sys

# Add project root to sys.path for internal imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

def parse_instruction(text, user_id="default"):
    engine = os.getenv("REASONING_ENGINE", "gemini").lower()
    
    # 1. Main Reasoning Engine (with Fallback)
    engines_to_try = [engine]
    if engine == "gemini":
        engines_to_try.append("claude_local")
    else:
        engines_to_try.append("gemini")

    for current_engine in engines_to_try:
        try:
            if current_engine == "gemini":
                from ronaldinho.skills.gemini_skill import analyze_instruction
                plan = analyze_instruction(text, user_id)
            elif current_engine == "claude_local":
                from ronaldinho.skills.claude_skill import analyze_instruction_local
                plan = analyze_instruction_local(text, user_id)
            else:
                continue

            if plan and "skill" in plan and "error" not in plan:
                return plan
        except Exception:
            continue

    text = text.lower()
    
    # Pattern: Create file
    create_match = re.search(r"crie (?:um )?arquivo chamado ['\"](.+?)['\"](?: com (?:o texto )?['\"](.+?)['\"])?", text)
    if create_match:
        filename = create_match.group(1)
        content = create_match.group(2) if create_match.group(2) else ""
        return {
            "skill": "file_skill",
            "action": "create",
            "args": [filename, content]
        }
    
    # ... (rest of regex patterns)
    
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
    uid = sys.argv[2] if len(sys.argv) > 2 else "default"
    result = parse_instruction(instruction, uid)
    if result:
        print(json.dumps(result))
    else:
        print(json.dumps({"error": "Instruction not understood"}))
