from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.orchestrator import Orchestrator
from app.config import settings
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
