import os
import sys
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load Environment
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=WORKSPACE_ROOT / ".env")

# Ollama / Local Claude Configuration
CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL", "http://localhost:11434/v1")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "qwen3-coder") # Recommendation for local coding tasks

def analyze_instruction_local(prompt, user_id="default"):
    """
    Simulates Claude-like reasoning using a local Ollama provider.
    Expected to be used with models like qwen3-coder or deepseek-v3.
    """
    
    system_prompt = """
    Você é o Ronaldinho, um agente de IA inteligente e prestativo.
    Sua personalidade é amigável, direta e focada em resolver tarefas.
    Não mencione que você é um modelo local — você é apenas o Ronaldinho.
    Converta instruções em JSON ou responda conversacionalmente de forma natural.

    AÇÕES DISPONÍVEIS:
    1. file_skill: create ([filename, content]), read ([filename]), list ([])
    2. orchestrator_skill: create ([script_name, content]), run ([script_name, *args])
    3. network_skill: curl ([url, method]), oauth ([service])
    4. context_skill: missions ([]), audit ([]), structure ([])

    Sempre responda APENAS o JSON:
    {"skill": "nome", "action": "acao", "args": []}
    OU se for conversa:
    {"skill": "gemini", "action": "chat", "args": ["Sua resposta natural aqui"]}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        # We use the OpenAI-compatible endpoint of Ollama
        response = requests.post(
            f"{CLAUDE_BASE_URL}/chat/completions",
            json={
                "model": CLAUDE_MODEL,
                "messages": messages,
                "temperature": 0.1,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return {"error": f"Ollama Error ({response.status_code}): {response.text}"}
            
        data = response.json()
        text = data['choices'][0]['message']['content'].strip()
        
        # Simple extraction
        if "{" in text and "}" in text:
            json_text = text[text.find("{"):text.rfind("}")+1]
            return json.loads(json_text)
        else:
            return {"skill": "gemini", "action": "chat", "args": [text]}
            
    except Exception as e:
        return {"error": f"Failed to connect to local Claude/Ollama: {e}"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No prompt provided"}))
        sys.exit(0)
    
    prompt = sys.argv[1]
    result = analyze_instruction_local(prompt)
    print(json.dumps(result))
