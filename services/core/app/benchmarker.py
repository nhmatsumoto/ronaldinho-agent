import time
import asyncio
import httpx
from app.config import settings

async def ping_provider(provider_name: str, url: str, api_key: str) -> float:
    """Pings a provider to measure latency. Returns latency in seconds or 999 if failed."""
    if not api_key:
        return 999.0
        
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            # Simple health check or minimalist request
            # For Gemini/NVIDIA we might need specific endpoints, but many support a basic GET or HEAD
            # Alternatively, we can do a very small 'Hello' prompt
            # For speed, we'll try to reach the base API endpoint
            response = await client.get(url, timeout=2.0)
            # Many APIs return 404 or 401 on base URL but are reachable
            # We just want to see if the server responds at all
            latency = time.perf_counter() - start_time
            return latency
    except Exception:
        return 999.0

async def get_latencies():
    """Concurrently pings all configured providers."""
    providers = {
        "gemini": ("https://generativelanguage.googleapis.com", settings.GEMINI_API_KEY),
        "openai": ("https://api.openai.com/v1/models", settings.OPENAI_API_KEY),
        "anthropic": ("https://api.anthropic.com/v1/messages", settings.ANTHROPIC_API_KEY),
        "nvidia": ("https://integrate.api.nvidia.com/v1", settings.NVIDIA_API_KEY),
        "groq": ("https://api.groq.com/openai/v1", settings.GROQ_API_KEY),
        "cerebras": ("https://api.cerebras.ai/v1", settings.CEREBRAS_API_KEY),
        "sambanova": ("https://api.sambanova.ai/v1", settings.SAMBANOVA_API_KEY),
        "openrouter": ("https://openrouter.ai/api/v1", settings.OPENROUTER_API_KEY),
        "mistral": ("https://api.mistral.ai/v1", settings.MISTRAL_API_KEY)
    }
    
    tasks = []
    names = []
    for name, (url, key) in providers.items():
        if key:
            tasks.append(ping_provider(name, url, key))
            names.append(name)
            
    if not tasks:
        return {}
        
    results = await asyncio.gather(*tasks)
    return dict(zip(names, results))

def get_fastest_provider(latencies: dict) -> str:
    """Returns the provider name with the lowest latency."""
    if not latencies:
        return settings.LLM_PROVIDER
        
    # Filter out failures
    valid = {k: v for k, v in latencies.items() if v < 999.0}
    if not valid:
        return settings.LLM_PROVIDER
        
    return min(valid, key=valid.get)
