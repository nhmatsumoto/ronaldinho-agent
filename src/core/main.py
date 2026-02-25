from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import Orchestrator
from config import settings
from auth import auth_manager
from vault import vault
import uvicorn
import os

app = FastAPI(title="Ronaldinho Neural Core (Python)")

# Enable CORS for Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

class MessageRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    platform: str = "web"

class ConfigUpdateRequest(BaseModel):
    keys: dict

@app.get("/health")
async def health_check():
    provider = settings.LLM_PROVIDER
    team_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/team"))
    browser_session = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/browser_session"))
    
    has_browser_session = os.path.exists(browser_session) and len(os.listdir(browser_session)) > 1
    
    return {
        "status": "ok", 
        "service": "neural-core",
        "version": "1.0.1",
        "llm_provider": provider,
        "benchmarking": settings.ENABLE_BENCHMARKING,
        "active_team_count": len(os.listdir(team_path)) if os.path.exists(team_path) else 0,
        "browser_ghost_mode": "active" if has_browser_session else "logged_out",
        "telegram_active": bool(settings.TELEGRAM_BOT_TOKEN)
    }

@app.get("/api/config")
async def get_config():
    """Returns current sanitized config."""
    # Only return keys we want the user to see/edit
    return {
        "GEMINI_API_KEY": settings.GEMINI_API_KEY[:8] + "..." if settings.GEMINI_API_KEY else "",
        "OPENAI_API_KEY": settings.OPENAI_API_KEY[:8] + "..." if settings.OPENAI_API_KEY else "",
        "NVIDIA_API_KEY": settings.NVIDIA_API_KEY[:8] + "..." if settings.NVIDIA_API_KEY else "",
        "TELEGRAM_BOT_TOKEN": settings.TELEGRAM_BOT_TOKEN[:8] + "..." if settings.TELEGRAM_BOT_TOKEN else "",
        "LLM_PROVIDER": settings.LLM_PROVIDER,
        "MODEL_PRIORITY": settings.MODEL_PRIORITY
    }

@app.post("/api/config/save")
async def save_config(request: ConfigUpdateRequest):
    """Saves new keys to .env and reloads settings (simulated)."""
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    
    # Read existing .env
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
    updated_keys = request.keys
    new_lines = []
    
    # Simple .env update logic
    seen_keys = set()
    for line in lines:
        matched = False
        for k, v in updated_keys.items():
            if line.startswith(f"{k}="):
                if v and not v.endswith("..."): # Only update if it's a real new key (not redacted)
                    new_lines.append(f"{k}={v}\n")
                    seen_keys.add(k)
                    matched = True
                    break
        if not matched:
            new_lines.append(line)
            
    for k, v in updated_keys.items():
        if k not in seen_keys and v and not v.endswith("..."):
            new_lines.append(f"{k}={v}\n")
            
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
        
    # Update settings in memory
    for k, v in updated_keys.items():
        if v and not v.endswith("..."):
            if hasattr(settings, k):
                setattr(settings, k, v)
        
    return {"status": "success", "message": "Configurações salvas e aplicadas em tempo real (Core)."}

@app.post("/api/chat")
async def chat(request: MessageRequest):
    try:
        # Orchestrator handles dynamic model/skill selection internally
        response = await orchestrator.process_message(request.message)
        return {"response": response}
    except Exception as e:
        error_msg = str(e)
        print(f"[!] Error in chat: {error_msg}")
        status_code = 429 if "quota" in error_msg.lower() or "429" in error_msg else 503
        raise HTTPException(status_code=status_code, detail=error_msg)

# --- Antigravity Integration Endpoints ---

@app.post("/api/antigravity/instruction")
async def antigravity_instruction(request: MessageRequest):
    """Specialized endpoint for high-level instructions from Antigravity."""
    try:
        # Force the Antigravity Envoy persona
        response = await orchestrator.process_message(f"[ANTIGRAVITY_SIG] {request.message}")
        return {
            "origin": "Antigravity Global",
            "status": "integrated",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/antigravity/sync")
async def antigravity_sync():
    """Returns the current state of Ronaldinho for Antigravity synchronization."""
    team_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/team"))
    return {
        "soul": "integrated",
        "active_team_count": len(os.listdir(team_path)) if os.path.exists(team_path) else 0,
        "protocol": "PROTOCOL_ANTIGRAVITY.md found",
        "timestamp": settings.PORT # Simple check
    }

# --- OAuth2 Endpoints ---

@app.get("/api/auth/login/{provider}")
async def auth_login(provider: str):
    # Redirect back to the Dashboard so script.js can handle the code
    redirect_uri = "http://localhost:3000/index.html"
    try:
        url = auth_manager.get_login_url(provider, redirect_uri)
        if not url:
            raise HTTPException(status_code=400, detail="Provedor inválido")
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/auth/callback")
async def auth_callback(code: str, provider: str = "google"):
    # The redirect_uri must match what was sent to Google
    redirect_uri = "http://localhost:3000/index.html"
    token = await auth_manager.exchange_code(provider, code, redirect_uri)
    if not token:
        raise HTTPException(status_code=400, detail="Falha na autenticação")
    return {"status": "success", "message": f"Conectado ao {provider} com sucesso!"}

@app.get("/api/auth/status")
async def auth_status():
    return {"providers": vault.list_providers()}

@app.post("/api/browser/login")
async def browser_login():
    """Triggers the manual browser login script."""
    import subprocess
    try:
        # Run the script in the background to not block the API
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts/browser_login.sh"))
        subprocess.Popen(["bash", script_path], cwd=os.path.dirname(os.path.dirname(script_path)))
        return {"status": "success", "message": "Navegador de login aberto. Verifique sua barra de tarefas."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
