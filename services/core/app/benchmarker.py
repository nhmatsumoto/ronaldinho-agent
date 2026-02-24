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
            response = await client.get(url, timeout=2.0)
            latency = time.perf_counter() - start_time
            return latency
    except Exception:
        return 999.0

async def test_model_capability(provider_name: str, api_key: str) -> bool:
    """Sends a minimalist prompt to verify the API key and model availability."""
    if not api_key:
        return False
        
    try:
        async with httpx.AsyncClient() as client:
            if provider_name == "gemini":
                # Using v1beta for Gemini as per project settings, but checking if it's functional
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": "hi"}]}]}
                response = await client.post(url, json=payload, timeout=5.0)
                return response.status_code == 200
            
            elif provider_name == "nvidia":
                url = "https://integrate.api.nvidia.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}"}
                payload = {
                    "model": "meta/llama-3.1-8b-instruct",
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 5
                }
                response = await client.post(url, json=payload, headers=headers, timeout=5.0)
                return response.status_code == 200
            
            # Add other providers as needed...
            return True # Assume others are functional if we don't have a specific test yet
    except Exception:
        return False

async def get_latencies():
    """Concurrently pings and tests all configured providers."""
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
        
    ping_results = await asyncio.gather(*tasks)
    
    # Also check integrity for the top candidates
    latencies = dict(zip(names, ping_results))
    fastest_names = sorted([n for n in names if latencies[n] < 999.0], key=lambda n: latencies[n])[:3]
    
    integrity_tasks = [test_model_capability(name, providers[name][1]) for name in fastest_names]
    integrity_results = await asyncio.gather(*integrity_tasks)
    
    integrity_map = dict(zip(fastest_names, integrity_results))
    
    # Adjust latencies based on integrity
    final_results = {}
    for name in names:
        if name in integrity_map and not integrity_map[name]:
            final_results[name] = 999.0 # Mark as failed if integrity test failed
        else:
            final_results[name] = latencies[name]
            
    return final_results

def get_fastest_provider(latencies: dict) -> str:
    """Returns the provider name with the lowest latency."""
    if not latencies:
        return settings.LLM_PROVIDER
        
    # Filter out failures
    valid = {k: v for k, v in latencies.items() if v < 999.0}
    if not valid:
        return settings.LLM_PROVIDER
        
    return min(valid, key=valid.get)

if __name__ == "__main__":
    import json
    async def main():
        print("[*] Running Model Integrity Benchmarker...")
        lats = await get_latencies()
        print(json.dumps(lats, indent=2))
        print(f"[*] Best Provider: {get_fastest_provider(lats)}")
    asyncio.run(main())
