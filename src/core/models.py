import logging
import httpx
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from config import settings
from vault import vault

logger = logging.getLogger("neural-core")

# Models known to have separate or generous free tier quotas.
# Fixed names for pydantic-ai compatibility.
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
            # Attempting to use the model ID directly as pydantic-ai handles the prefix
            provider = GoogleGLAProvider(api_key=api_key)
            return GeminiModel(m_id, provider=provider)
        
        elif provider_name == "openai":
            api_key = settings.OPENAI_API_KEY
            if not api_key: return None
            provider = OpenAIProvider(api_key=api_key)
            return OpenAIChatModel(model_id or "gpt-4o", provider=provider)
        
        elif provider_name == "nvidia":
            if not settings.NVIDIA_API_KEY: return None
            # Standard NVIDIA IDs often use meta/ llama-3.1 etc
            m_id = model_id or "meta/llama-3.1-8b-instruct"
            provider = OpenAIProvider(api_key=settings.NVIDIA_API_KEY, base_url=settings.NVIDIA_BASE_URL)
            return OpenAIChatModel(m_id, provider=provider)
        
        elif provider_name == "groq":
            if not settings.GROQ_API_KEY: return None
            provider = OpenAIProvider(api_key=settings.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
            return OpenAIChatModel(model_id or "llama-3.3-70b-versatile", provider=provider)

    except Exception as e:
        logger.warning(f"[!] Error initializing provider {provider_name}: {e}")
    return None

def get_boot_model():
    priority = settings.MODEL_PRIORITY.split(",")
    for provider in priority:
        instance = get_model_instance(provider)
        if instance: return instance
    return "google-gla:gemini-2.0-flash"
