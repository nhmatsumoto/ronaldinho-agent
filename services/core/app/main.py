from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.orchestrator import Orchestrator
from app.config import settings
import uvicorn

app = FastAPI(title="Ronaldinho Neural Core (Python)")
orchestrator = Orchestrator()

class MessageRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    platform: str = "web"

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "neural-core-python"}

@app.post("/api/chat")
async def chat(request: MessageRequest):
    try:
        response = await orchestrator.process_message(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
