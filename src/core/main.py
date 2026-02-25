from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import Orchestrator
from config import settings
from auth import auth_manager
from vault import vault
from brain import clear_brain_cache
from skills_engine import skills_engine
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
    skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/skills"))
    
    has_browser_session = os.path.exists(browser_session) and len(os.listdir(browser_session)) > 1
    skills_count = len(os.listdir(skills_path)) if os.path.exists(skills_path) else 0
    
    return {
        "status": "ok", 
        "service": "neural-core",
        "edition": "openclaw-pro",
        "version": "1.0.1",
        "llm_provider": provider,
        "benchmarking": settings.ENABLE_BENCHMARKING,
        "active_team_count": len(os.listdir(team_path)) if os.path.exists(team_path) else 0,
        "active_skills_count": skills_count,
        "heartbeat": "active",
        "browser_ghost_mode": "active" if has_browser_session else "logged_out",
        "telegram_active": bool(settings.TELEGRAM_BOT_TOKEN)
    }

@app.get("/api/config")
async def get_config():
    """Returns current sanitized config."""
    return {
        "GEMINI_API_KEY": settings.GEMINI_API_KEY[:8] + "..." if settings.GEMINI_API_KEY else "",
        "OPENAI_API_KEY": settings.OPENAI_API_KEY[:8] + "..." if settings.OPENAI_API_KEY else "",
        "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY[:8] + "..." if settings.ANTHROPIC_API_KEY else "",
        "OPENROUTER_API_KEY": settings.OPENROUTER_API_KEY[:8] + "..." if settings.OPENROUTER_API_KEY else "",
        "NVIDIA_API_KEY": settings.NVIDIA_API_KEY[:8] + "..." if settings.NVIDIA_API_KEY else "",
        "TELEGRAM_BOT_TOKEN": settings.TELEGRAM_BOT_TOKEN[:8] + "..." if settings.TELEGRAM_BOT_TOKEN else "",
        "LLM_PROVIDER": settings.LLM_PROVIDER,
        "MODEL_PRIORITY": settings.MODEL_PRIORITY
    }

@app.get("/api/skills")
async def list_skills():
    """Lists all installed skills and their metadata."""
    skills_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/skills"))
    skills = []
    if os.path.exists(skills_path):
        for s in os.listdir(skills_path):
            if os.path.isdir(os.path.join(skills_path, s)):
                skills.append({
                    "id": s,
                    "name": s.replace("_", " ").title(),
                    "status": "active"
                })
    return {"skills": skills}

@app.post("/api/config/save")
async def save_config(request: ConfigUpdateRequest):
    """Saves new keys to .env and reloads settings."""
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
    updated_keys = request.keys
    new_lines = []
    seen_keys = set()
    
    for line in lines:
        matched = False
        for k, v in updated_keys.items():
            if line.startswith(f"{k}="):
                if v and not v.endswith("..."):
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
    
    clear_brain_cache()
    skills_engine.refresh_cache()
    return {"status": "success", "message": "Configurações salvas e aplicadas em tempo real (Core)."}

@app.post("/api/chat")
async def chat(request: MessageRequest):
    try:
        response = await orchestrator.process_message(request.message, user_id=request.user_id)
        return {"response": response}
    except Exception as e:
        error_msg = str(e)
        status_code = 429 if "quota" in error_msg.lower() or "429" in error_msg else 503
        raise HTTPException(status_code=status_code, detail=error_msg)

@app.get("/api/antigravity/sync")
async def antigravity_sync():
    team_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/team"))
    return {
        "soul": "integrated",
        "active_team_count": len(os.listdir(team_path)) if os.path.exists(team_path) else 0,
        "protocol": "PROTOCOL_ANTIGRAVITY.md found"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
