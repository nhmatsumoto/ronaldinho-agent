import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
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

HISTORY_FILE = WORKSPACE_ROOT / "ronaldinho" / "data" / "chat_history.json"

def connect_gemini(with_search=False, model_tier="1.5"):
    if not GEMINI_API_KEY or "your_gemini_api_key" in GEMINI_API_KEY:
        return None
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use Gemini 3 Flash as requested by user, fallback to 1.5 if needed
        model_name = "gemini-3-flash-preview" if model_tier == "3.0" else "gemini-flash-latest"
        
        tools = []
        if with_search:
             try:
                tools = [genai.protos.Tool(google_search_retrieval=genai.protos.GoogleSearchRetrieval())]
             except:
                pass

        model = genai.GenerativeModel(model_name, tools=tools)
        return model
    except Exception:
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
    mode = os.getenv("REASONING_MODE", "FAST").upper() # FAST or PLANNING
    
    # Check if prompt requires search
    requires_search = any(k in prompt.lower() for k in ["pesquise", "quem e", "valor do", "noticia", "hoje"])
    
    # Try 3.0 Tier first (Gemini 3 Flash Preview as requested)
    model = connect_gemini(with_search=requires_search, model_tier="3.0")
    if not model:
        return {"error": "Gemini API Key missing or unavailable."}

    planning_addon = ""
    if mode == "PLANNING":
        planning_addon = "Pense passo a passo antes de decidir a ação. Analise se precisa criar ferramentas ou ler arquivos primeiro."

    system_prompt = f"""
    Você é o Ronaldinho, um agente de IA inteligente e prestativo.
    Sua personalidade é amigável, direta e focada em resolver tarefas.
    {planning_addon}
    Converta instruções em JSON ou responda conversacionalmente de forma natural.

    Ações disponíveis:
    1. file_skill: create ([filename, content]), read ([filename]), list ([]), send ([filename])
    2. orchestrator_skill: create ([script_name, content]), run ([script_name, *args])
    3. network_skill: curl ([url, method]), oauth ([service])
    4. context_skill: missions ([]), audit ([]), structure ([])

    Sempre responda APENAS o JSON:
    {{"skill": "nome", "action": "acao", "args": []}}
    OU se for conversa:
    {{"skill": "gemini", "action": "chat", "args": ["Sua resposta natural aqui"]}}
    """

    messages = [{"role": "user", "parts": [system_prompt]}]
    for h in history:
        messages.append(h)
    messages.append({"role": "user", "parts": [prompt]})

    try:
        response = model.generate_content(messages)
    except Exception as e:
        # Fallback to 1.5 if 2.0 is over quota
        if "429" in str(e) or "quota" in str(e).lower():
            # Fallback to model_tier="1.5" which points to models/gemini-flash-latest
            model_15 = connect_gemini(with_search=requires_search, model_tier="1.5")
            if model_15:
                try:
                    response = model_15.generate_content(messages)
                except Exception as e2:
                    return {"error": f"Gemini 3.0 and 1.5 exhausted: {e2}"}
            else:
                return {"error": f"Gemini 3.0 exhausted and 1.5 unavailable: {e}"}
        else:
            return {"error": f"Gemini Error: {e}"}
    
    try:
        # Clean the response - sometimes it comes with backticks or "json"
        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
        plan = json.loads(response_text)
        
        # Add to history
        history.append({"role": "user", "parts": [prompt]}) # Add user prompt to history
        history.append({"role": "model", "parts": [response_text]})
        save_history(user_id, history)
        
        return plan
    except Exception as e:
        return {"error": f"Failed to parse JSON response: {e}. Raw: {response.text[:100]}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No prompt provided"}))
        sys.exit(0)
    
    prompt = sys.argv[1]
    uid = sys.argv[2] if len(sys.argv) > 2 else "default"
    result = analyze_instruction(prompt, uid)
    print(json.dumps(result))
