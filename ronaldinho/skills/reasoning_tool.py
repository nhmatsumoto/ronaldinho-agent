import re
import os
import sys

# Add project root to sys.path for internal imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_path not in sys.path:
    sys.path.append(root_path)

def parse_instruction(text, user_id="default"):
    # Try Gemini Reasoning first
    try:
        from ronaldinho.skills.gemini_skill import analyze_instruction
        plan = analyze_instruction(text, user_id)
        if plan:
            if "error" in plan:
                print(f"DEBUG: Gemini Logic Error: {plan['error']}")
            if "skill" in plan and "error" not in plan:
                return plan
    except Exception as e:
        # Fallback to Regex if Gemini fails
        print(f"DEBUG: Gemini Exception: {e}")
        pass

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
