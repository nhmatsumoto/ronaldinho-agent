from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.orchestrator import Orchestrator
from app.config import settings
from app.auth import auth_manager
from app.vault import vault
import uvicorn

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

@app.get("/health")
async def health_check():
    provider = settings.LLM_PROVIDER
    return {
        "status": "ok", 
        "service": "neural-core",
        "version": "1.0.1",
        "llm_provider": provider,
        "benchmarking": settings.ENABLE_BENCHMARKING
    }

@app.post("/api/chat")
async def chat(request: MessageRequest):
    try:
        # Orchestrator handles dynamic model/skill selection internally
        response = await orchestrator.process_message(request.message)
        return {"response": response}
    except Exception as e:
        error_msg = str(e)
        print(f"[!] Error in chat: {error_msg}")
        raise HTTPException(status_code=503, detail=error_msg)

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
