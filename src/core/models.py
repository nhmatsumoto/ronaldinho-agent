import logging
import httpx
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from config import settings
from vault import vault

logger = logging.getLogger("neural-core")

# Unified rotation for all agents
GEMINI_ROTATION_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash", 
    "gemini-1.5-pro"
]

def get_model_instance(provider_name: str, model_id: str = None):
    """
    Unified gateway to fetch specialized model instances.
    Matches OpenClaw's model-agnostic approach.
    """
    try:
        # 1. GOOGLE GEMINI
        if provider_name == "gemini":
            api_key = settings.GEMINI_API_KEY
            if not api_key: return None
            provider = GoogleGLAProvider(api_key=api_key)
            return GeminiModel(model_id or "gemini-2.0-flash", provider=provider)
        
        # 2. OPENAI (Direct or OpenRouter via base_url)
        elif provider_name == "openai" or provider_name == "openrouter":
            api_key = settings.OPENAI_API_KEY
            base_url = "https://openrouter.ai/api/v1" if provider_name == "openrouter" else None
            if not api_key: return None
            provider = OpenAIProvider(api_key=api_key, base_url=base_url)
            return OpenAIChatModel(model_id or "gpt-4o", provider=provider)

        # 3. ANTHROPIC CLAUDE
        elif provider_name == "anthropic":
            api_key = settings.ANTHROPIC_API_KEY
            if not api_key: return None
            provider = AnthropicProvider(api_key=api_key)
            return AnthropicModel(model_id or "claude-3-5-sonnet-latest", provider=provider)

        # 4. NVIDIA NIM (Standard OpenAI compatible)
        elif provider_name == "nvidia":
            api_key = settings.NVIDIA_API_KEY
            if not api_key: return None
            provider = OpenAIProvider(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")
            return OpenAIChatModel(model_id or "meta/llama-3.1-405b-instruct", provider=provider)

    except Exception as e:
        logger.warning(f"[!] Error initializing provider {provider_name}: {e}")
    return None

def get_boot_model():
    """Fallback logic to find at least one working model for initialization."""
    priority = settings.MODEL_PRIORITY.split(",")
    for p in priority:
        instance = get_model_instance(p)
        if instance: return instance
    return "google-gla:gemini-2.0-flash"
