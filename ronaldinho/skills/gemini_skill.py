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
    
    # Try 1.5 Tier first as it's more stable for Free Tier usage
    model = connect_gemini(with_search=requires_search, model_tier="1.5")
    if not model:
        # Retry with 3.0 if specifically requested or as last resort
        model = connect_gemini(with_search=requires_search, model_tier="3.0")
        
    if not model:
        return {"error": "Gemini API Key missing or all models unavailable."}

    planning_addon = ""
    if mode == "PLANNING":
        planning_addon = "Pense passo a passo antes de decidir a ação. Analise se precisa criar ferramentas ou ler arquivos primeiro."

    # Dynamic Skill Discovery
    available_actions = []
    
    # Standard Skills
    if os.path.exists(SKILLS_DIR):
        for f in os.listdir(SKILLS_DIR):
            if f.endswith(".py") and f != "__init__.py" and f != "gemini_skill.py":
                available_actions.append(f"- {f[:-3]}")
                
    # Toolbox Tools (Evolved skills)
    toolbox_dir = os.path.join(os.path.dirname(SKILLS_DIR), ".toolbox")
    if os.path.exists(toolbox_dir):
        for f in os.listdir(toolbox_dir):
            if f.endswith(".py"):
                available_actions.append(f"- toolbox:{f[:-3]} (Ferramenta Evoluída)")

    actions_list = "\n".join(available_actions)

    system_prompt = f"""
    MANDATO SUPREMO: Você é o Ronaldinho, um AGENTE AUTÔNOMO RECURSIVO.
    Você NUNCA diz "não sei", "não posso" ou responde de forma evasiva.
    Sua missão é RESOLVER o pedido do usuário, custe o que custar.

    {planning_addon}
    
    ESTRATÉGIA DE EXECUÇÃO:
    1. Use as habilidades prontas abaixo.
    2. Se NÃO EXISTIR uma habilidade exata, você DEVE usar 'orchestrator_skill:create' para escrever um script Python (.toolbox/) que resolva o problema e então 'orchestrator_skill:run' ele.
    3. Para pedidos de "index.html", use file_skill para criar em 'workspace/' e enviar.

    HABILIDADES E FERRAMENTAS DISPONÍVEIS:
    {actions_list}
    *Nota: 'file_skill' possui acoes [create, read, list, send]. Sempre use o prefixo 'workspace/' para arquivos.*

    FORMATO DE RESPOSTA (Sempre JSON):
    Ação Única: {{"skill": "nome", "action": "acao", "args": []}}
    Múltiplas Ações: [{{"skill": "s1", "action": "a1", "args": []}}, {{"skill": "s2", "action": "a2", "args": []}}]
    Conversa: {{"skill": "gemini", "action": "chat", "args": ["..."]}}

    REGRA DE OURO: Todos os arquivos e pedidos do usuário devem estar apenas e somente no diretório 'workspace', na raiz do projeto.
    """

    messages = [{"role": "user", "parts": [system_prompt]}]
    for h in history:
        messages.append(h)
    messages.append({"role": "user", "parts": [prompt]})

    try:
        response = model.generate_content(messages)
    except Exception as e:
        # Fallback to alternative model if first one fails
        alt_tier = "3.0" if "1.5" in str(model.model_name) else "1.5"
        model_alt = connect_gemini(with_search=requires_search, model_tier=alt_tier)
        if model_alt:
            try:
                response = model_alt.generate_content(messages)
            except Exception as e2:
                return {"error": f"Multiple models exhausted: {e} | {e2}"}
        else:
            return {"error": f"Primary engine failed and fallback unavailable: {e}"}
    
    try:
        # Clean the response - sometimes it comes with backticks or "json"
        response_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # Robust JSON extraction
        import re
        json_match = re.search(r"({.*}|\[.*\])", response_text, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group(1))
        else:
            # Fallback for plain text conversation
            plan = {"skill": "gemini", "action": "chat", "args": [response_text]}
            
        # Add to history
        history.append({"role": "user", "parts": [prompt]}) 
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
