import logging
import httpx
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from config import settings
from vault import vault

logger = logging.getLogger("neural-core")

# Using plain IDs as gemini-2.0-flash worked (gave 429 instead of 404)
GEMINI_ROTATION_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash", 
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro"
]

def get_model_instance(provider_name: str, model_id: str = None):
    try:
        if provider_name == "gemini":
            user_token = vault.get_token("google")
            api_key = user_token.get("access_token") if user_token else settings.GEMINI_API_KEY
            if not api_key: return None
            
            m_id = model_id or "gemini-2.0-flash"
            provider = GoogleGLAProvider(api_key=api_key)
            return GeminiModel(m_id, provider=provider)
        
    except Exception as e:
        logger.warning(f"[!] Error initializing provider {provider_name}: {e}")
    return None

def get_boot_model():
    instance = get_model_instance("gemini")
    if instance: return instance
    return "google-gla:gemini-2.0-flash"
