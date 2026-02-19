import os
import sys
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load API Key
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
env_path = WORKSPACE_ROOT / ".env"
load_dotenv(dotenv_path=env_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
HISTORY_FILE = WORKSPACE_ROOT / "workspace" / "data" / "chat_history.json"

def connect_gemini(with_search=False):
    if not GEMINI_API_KEY or "your_gemini_api_key" in GEMINI_API_KEY:
        print(f"DEBUG: Invalid API Key: {GEMINI_API_KEY[:10]}...", file=sys.stderr)
        return None
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model_name = "gemini-1.5-flash"
        
        tools = []
        if with_search:
             try:
                tools = [genai.protos.Tool(google_search_retrieval=genai.protos.GoogleSearchRetrieval())]
             except:
                print("DEBUG: Google Search tool not available in this SDK version.", file=sys.stderr)

        model = genai.GenerativeModel(model_name, tools=tools)
        return model
    except Exception as e:
        print(f"DEBUG: Gemini Connection Error: {e}", file=sys.stderr)
        return None

def load_history(user_id):
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(str(user_id), [])
    except:
        return []

def save_history(user_id, history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            pass
    
    data[str(user_id)] = history[-10:] # Keep last 10 messages
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def analyze_instruction(prompt, user_id="default"):
    history = load_history(user_id)
    
    # Check if prompt requires search
    requires_search = any(k in prompt.lower() for k in ["pesquise", "quem e", "valor do", "noticia", "hoje"])
    
    model = connect_gemini(with_search=requires_search)
    if not model:
        return {"error": "Gemini API Key missing or model unavailable."}

    system_prompt = """
    Você é o cérebro do Ronaldinho-Agent (Modo Antigravity).
    Converta instruções em JSON ou responda conversacionalmente.
    Ações disponíveis:
    1. file_skill: create ([filename, content]), read ([filename]), list ([])
    2. orchestrator_skill: create ([script_name, content]), run ([script_name, *args])
    3. network_skill: curl ([url, method]), oauth ([service])
    4. context_skill: missions ([]), audit ([]), structure ([])

    Sempre responda APENAS o JSON:
    {"skill": "nome", "action": "acao", "args": []}
    OU se for conversa:
    {"skill": "gemini", "action": "chat", "args": ["Resposta"]}
    """

    messages = [{"role": "user", "parts": [system_prompt]}]
    for h in history:
        messages.append(h)
    messages.append({"role": "user", "parts": [prompt]})

    try:
        response = model.generate_content(messages)
        text = response.text.strip()
        
        # Simple extraction
        if "{" in text and "}" in text:
            json_text = text[text.find("{"):text.rfind("}")+1]
            result = json.loads(json_text)
        else:
            result = {"skill": "gemini", "action": "chat", "args": [text]}
        
        # Update history
        history.append({"role": "user", "parts": [prompt]})
        history.append({"role": "model", "parts": [text]})
        save_history(user_id, history)
        
        return result
    except Exception as e:
        return {"error": f"Failed to generate reasoning: {e}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No prompt provided"}))
        sys.exit(0)
    
    prompt = sys.argv[1]
    uid = sys.argv[2] if len(sys.argv) > 2 else "default"
    result = analyze_instruction(prompt, uid)
    print(json.dumps(result))
