from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.groq import GroqProvider
from app.config import settings
from app.tools.terminal import TerminalTool
from app.tools.editor import EditorTool
import os
import logging

# Setup Logging
logger = logging.getLogger("neural-core")

# Initialize Tools
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
terminal = TerminalTool(root_path)
editor = EditorTool(root_path)

from app.skills import get_integrated_system_prompt
from app.benchmarker import get_latencies, get_fastest_provider

def get_model_instance(provider_name: str, model_id: str = None):
    """Returns a PydanticAI Model instance for the given provider."""
    try:
        if provider_name == "gemini":
            gla_provider = GoogleGLAProvider(api_key=settings.GEMINI_API_KEY)
            return GeminiModel(model_id or "gemini-1.5-pro", provider=gla_provider)
        
        elif provider_name == "openai":
            if not settings.OPENAI_API_KEY: return None
            oa_provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            return OpenAIChatModel(model_id or "gpt-4o", provider=oa_provider)
        
        elif provider_name == "anthropic":
            if not settings.ANTHROPIC_API_KEY: return None
            ant_provider = AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
            return AnthropicModel(model_id or "claude-3-5-sonnet-latest", provider=ant_provider)
        
        elif provider_name == "nvidia":
            if not settings.NVIDIA_API_KEY: return None
            nv_provider = OpenAIProvider(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=settings.NVIDIA_API_KEY
            )
            return OpenAIChatModel(model_id or settings.NVIDIA_MODEL_ID, provider=nv_provider)
        
        elif provider_name == "groq":
            if not settings.GROQ_API_KEY: return None
            gr_provider = OpenAIProvider(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )
            return OpenAIChatModel(model_id or "llama-3.3-70b-versatile", provider=gr_provider)
                
        elif provider_name == "cerebras":
            if not settings.CEREBRAS_API_KEY: return None
            cb_provider = OpenAIProvider(
                base_url="https://api.cerebras.ai/v1",
                api_key=settings.CEREBRAS_API_KEY
            )
            return OpenAIChatModel(model_id or "llama3.1-70b", provider=cb_provider)
            
        elif provider_name == "sambanova":
            if not settings.SAMBANOVA_API_KEY: return None
            sn_provider = OpenAIProvider(
                base_url="https://api.sambanova.ai/v1",
                api_key=settings.SAMBANOVA_API_KEY
            )
            return OpenAIChatModel(model_id or "llama3-70b", provider=sn_provider)
            
        elif provider_name == "openrouter":
            if not settings.OPENROUTER_API_KEY: return None
            or_provider = OpenAIProvider(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY
            )
            return OpenAIChatModel(model_id or "auto", provider=or_provider)
            
        elif provider_name == "mistral":
            if not settings.MISTRAL_API_KEY: return None
            ms_provider = OpenAIProvider(
                base_url="https://api.mistral.ai/v1",
                api_key=settings.MISTRAL_API_KEY
            )
            return OpenAIChatModel(model_id or "codestral-latest", provider=ms_provider)
    except Exception as e:
        logger.warning(f"[!] Failed to initialize provider {provider_name}: {e}")
        return None
        
    return None

# Helper to pick a safe model for initial boot (synchronous)
def get_boot_model():
    priority = settings.MODEL_PRIORITY.split(",")
    for provider in priority:
        instance = get_model_instance(provider)
        if instance:
            return instance
    # Ultimate fallback 
    return GeminiModel("gemini-1.5-pro", provider=GoogleGLAProvider(api_key="dummy"))

async def get_dynamic_model(is_coding_task: bool = False):
    if is_coding_task and settings.NVIDIA_API_KEY:
        instance = get_model_instance("nvidia", model_id="meta/llama-3.1-405b-instruct")
        if instance: return instance
        
    if settings.ENABLE_BENCHMARKING:
        try:
            latencies = await get_latencies()
            fastest = get_fastest_provider(latencies)
            instance = get_model_instance(fastest)
            if instance: return instance
        except Exception:
            pass

    return get_boot_model()

# Initialize Agent
system_prompt = get_integrated_system_prompt(root_path)
agent = Agent(
    get_boot_model(),
    system_prompt=system_prompt
)

@agent.tool
def run_command(ctx: RunContext[None], command: str) -> str:
    """Executa um comando no terminal do sistema."""
    return terminal.execute(command)

@agent.tool
def read_file(ctx: RunContext[None], path: str) -> str:
    """Lê o conteúdo de um arquivo."""
    return editor.read_file(path)

@agent.tool
def write_file(ctx: RunContext[None], path: str, content: str) -> str:
    """Escreve conteúdo em um arquivo."""
    return editor.write_file(path, content)

@agent.tool
def list_files(ctx: RunContext[None], directory: str = ".") -> str:
    """Lista arquivos em um diretório."""
    return editor.list_files(directory)

class Orchestrator:
    async def process_message(self, message: str) -> str:
        coding_keywords = ["escreva um código", "refatore", "bug", "fix", "python", "javascript", "code"]
        is_coding = any(kw in message.lower() for kw in coding_keywords)
        
        # Try dynamic model first
        try:
            model = await get_dynamic_model(is_coding_task=is_coding)
            result = await agent.run(message, model=model)
            return result.data
        except Exception as e:
            logger.warning(f"[!] Primary model failed: {e}. Trying fallbacks...")
            
            # Runtime Fallback: Iterate through all priority models
            priority = settings.MODEL_PRIORITY.split(",")
            for provider_name in priority:
                fallback_model = get_model_instance(provider_name)
                if not fallback_model:
                    continue
                
                try:
                    logger.info(f"[*] Attempting fallback with: {provider_name}")
                    result = await agent.run(message, model=fallback_model)
                    return result.data
                except Exception as ef:
                    logger.warning(f"[!] Fallback {provider_name} also failed: {ef}")
                    continue
            
            raise Exception("Todos os modelos (incluindo fallbacks) falharam. Verifique suas chaves de API.")
