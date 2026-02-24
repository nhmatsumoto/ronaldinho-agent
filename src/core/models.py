import logging
import httpx
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.gemini import GeminiModel as PydanticGeminiModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from .config import settings
from .vault import vault

logger = logging.getLogger("neural-core")

class CustomGeminiModel(PydanticGeminiModel):
    async def generate(self, prompt: str) -> str:
        api_key = self.provider.get_api_key()
        if not api_key: raise ValueError("No API Key")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={api_key}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30.0)
                if response.status_code == 429:
                    raise Exception(f"Quota Exceeded (429) for {self.model_id}")
                if response.status_code != 200:
                    raise Exception(f"Gemini API Error {response.status_code}: {response.text}")
                
                data = response.json()
                if 'candidates' not in data or not data['candidates']:
                    raise Exception(f"Gemini API returned no candidates: {data}")
                
                return data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                raise e

GEMINI_ROTATION_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash", 
    "gemini-1.5-pro",
    "gemini-2.5-flash"
]

def get_model_instance(provider_name: str, model_id: str = None):
    try:
        if provider_name == "gemini":
            user_token = vault.get_token("google")
            api_key = user_token.get("access_token") if user_token else settings.GEMINI_API_KEY
            if not api_key: return None
            gla_provider = GoogleGLAProvider(api_key=api_key)
            return CustomGeminiModel(model_id or "gemini-2.0-flash", provider=gla_provider)
        
        elif provider_name == "openai":
            user_token = vault.get_token("openai")
            api_key = user_token.get("access_token") if user_token else settings.OPENAI_API_KEY
            if not api_key: return None
            oa_provider = OpenAIProvider(api_key=api_key)
            return OpenAIChatModel(model_id or "gpt-4o", provider=oa_provider)
        
        elif provider_name == "anthropic":
            if not settings.ANTHROPIC_API_KEY: return None
            ant_provider = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
            return AnthropicModel(model_id or "claude-3-5-sonnet-latest", provider=ant_provider)
        
        elif provider_name == "nvidia":
            if not settings.NVIDIA_API_KEY: return None
            nv_provider = OpenAIProvider(base_url=settings.NVIDIA_BASE_URL, api_key=settings.NVIDIA_API_KEY)
            return OpenAIChatModel(model_id or settings.NVIDIA_MODEL_ID, provider=nv_provider)
        
        elif provider_name == "groq":
            if not settings.GROQ_API_KEY: return None
            gr_provider = OpenAIProvider(base_url="https://api.groq.com/openai/v1", api_key=settings.GROQ_API_KEY)
            return OpenAIChatModel(model_id or "llama-3.3-70b-versatile", provider=gr_provider)

        # Fallback to SambaNova, OpenRouter, etc. can be added here
    except Exception as e:
        logger.warning(f"[!] Error initializing provider {provider_name}: {e}")
    return None

def get_boot_model():
    priority = settings.MODEL_PRIORITY.split(",")
    for provider in priority:
        instance = get_model_instance(provider)
        if instance: return instance
    return None
