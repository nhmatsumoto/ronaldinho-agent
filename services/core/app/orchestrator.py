from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.gemini import GeminiModel as PydanticGeminiModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.groq import GroqProvider
from app.config import settings
from app.tools.terminal import TerminalTool
from app.tools.editor import EditorTool
from app.tools.dev_toolkit import DevToolkit
import os
import logging

# Setup Logging
logger = logging.getLogger("neural-core")

# Initialize Tools
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
terminal = TerminalTool(root_path)
editor = EditorTool(root_path)
dev_toolkit = DevToolkit(root_path)

from app.skills import get_integrated_system_prompt
from app.benchmarker import get_latencies, get_fastest_provider
from app.gemini_cli_local import gemini_cli
from app.vault import vault
from app.evolution_logger import evolution_logger
import random
import httpx

# Custom GeminiModel to handle exceptions and quota detection
class CustomGeminiModel(PydanticGeminiModel):
    async def generate(self, prompt: str) -> str:
        api_key = self.provider.get_api_key()
        if not api_key: raise ValueError("No API Key")
        
        # Use v1beta for better model support/preview IDs
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

# Models to rotate through when Gemini hits limits
GEMINI_ROTATION_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash", 
    "gemini-1.5-pro",
    "gemini-2.5-flash" # User reported this exists and works
]

def get_model_instance(provider_name: str, model_id: str = None):
    """Returns a PydanticAI Model instance for the given provider, or None if config is missing."""
    try:
        if provider_name == "gemini":
            # Check vault for user token
            user_token = vault.get_token("google")
            api_key = user_token.get("access_token") if user_token else settings.GEMINI_API_KEY
            if not api_key: return None
            
            try:
                gla_provider = GoogleGLAProvider(api_key=api_key)
                # We default to a stable model but rotation will swap it if it fails
                return CustomGeminiModel(model_id or "gemini-2.0-flash", provider=gla_provider)
            except Exception: return None
        
        elif provider_name == "openai":
            # Check vault for user token
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
            nv_provider = OpenAIProvider(
                base_url=settings.NVIDIA_BASE_URL,
                api_key=settings.NVIDIA_API_KEY
            )
            return OpenAIChatModel(model_id or settings.NVIDIA_MODEL_ID, provider=nv_provider)
        
        elif provider_name == "nim":
            if not settings.NIM_BASE_URL: return None
            nim_provider = OpenAIProvider(
                base_url=settings.NIM_BASE_URL,
                api_key=settings.NIM_API_KEY
            )
            return OpenAIChatModel(model_id or "local-nim", provider=nim_provider)
        
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
        logger.warning(f"[!] Critical error initializing provider {provider_name}: {e}")
        return None
        
    return None

# Helper to pick a safe model for initial boot (synchronous)
def get_boot_model():
    priority = settings.MODEL_PRIORITY.split(",")
    for provider in priority:
        instance = get_model_instance(provider)
        if instance:
            return instance
    
    # If NO models are configured, we return a special placeholder that will fail helpfully at runtime
    # instead of crashing the process at boot.
    return None

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
# Handle the case where get_boot_model() might return None
boot_model = get_boot_model()
agent = Agent(
    boot_model or CustomGeminiModel("gemini-2.0-flash", provider=GoogleGLAProvider(api_key="placeholder")),
    system_prompt=system_prompt
)

# --- Standard Tools ---
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

# --- Dev Tools ---
@agent.tool
def git_status(ctx: RunContext[None]) -> str:
    """Retorna o status do git no repositório."""
    return dev_toolkit.get_git_status()

@agent.tool
def git_commit(ctx: RunContext[None], message: str) -> str:
    """Realiza um commit com as mudanças atuais."""
    return dev_toolkit.git_commit(message)

@agent.tool
def docker_ps(ctx: RunContext[None]) -> str:
    """Lista containers docker em execução."""
    return dev_toolkit.docker_ps()

@agent.tool
def docker_logs(ctx: RunContext[None], container: str) -> str:
    """Pega os logs de um container específico."""
    return dev_toolkit.docker_logs(container)

@agent.tool
def lint_file(ctx: RunContext[None], path: str) -> str:
    """Analisa a qualidade do código de um arquivo."""
    return dev_toolkit.check_lint(path)

@agent.tool
def format_file(ctx: RunContext[None], path: str) -> str:
    """Formata o código de um arquivo."""
    return dev_toolkit.format_code(path)

@agent.tool
def python_sandbox(ctx: RunContext[None], code: str) -> str:
    """Executa código Python em um ambiente Docker isolado e seguro. Use para testar lógica, validar sintaxe ou resolver problemas complexos com scripts temporários."""
    return dev_toolkit.run_python_sandbox(code)

class Orchestrator:
    async def process_message(self, message: str) -> str:
        coding_keywords = ["escreva um código", "refatore", "bug", "fix", "python", "javascript", "code", "docker", "git", "commit", "planeje", "implemente"]
        is_coding = any(kw in message.lower() for kw in coding_keywords)
        
        # Priority list of models to try
        tried_combinations = [] # list of (provider, model_id)
        
        # 1. Start with the "Recommended" provider from Benchmarker/Settings
        try:
            primary_model = await get_dynamic_model(is_coding_task=is_coding)
            if primary_model:
                try:
                    p_name = "gemini" if isinstance(primary_model, CustomGeminiModel) else "other"
                    p_id = getattr(primary_model, 'model_id', 'unknown')
                    
                    result = await agent.run(message, model=primary_model)
                    evolution_logger.log_event(p_name, p_id, "SUCCESS")
                    return result.data
                except Exception as e:
                    logger.warning(f"[!] Primary model failed: {e}. Starting rotation...")
                    evolution_logger.log_event("dynamic", "primary", "FAILURE", error=str(e))
        except Exception as e:
            logger.error(f"[!] Error getting dynamic model: {e}")

        # 2. Rotation Loop
        priority = settings.MODEL_PRIORITY.split(",")
        for provider_name in priority:
            # Special logic for Gemini: Rotate through several IDs
            if provider_name == "gemini":
                for model_id in GEMINI_ROTATION_MODELS:
                    try:
                        fallback_model = get_model_instance(provider_name, model_id=model_id)
                        if not fallback_model: continue
                        
                        logger.info(f"[*] Attempting fallback: {provider_name} | {model_id}")
                        result = await agent.run(message, model=fallback_model)
                        evolution_logger.log_event(provider_name, model_id, "SUCCESS")
                        return result.data
                    except Exception as ef:
                        logger.warning(f"[!] {provider_name} | {model_id} failed: {ef}")
                        evolution_logger.log_event(provider_name, model_id, "FAILURE", error=str(ef))
                        continue
            else:
                # Standard fallback for other providers
                try:
                    fallback_model = get_model_instance(provider_name)
                    if not fallback_model: continue
                    
                    f_id = getattr(fallback_model, 'model_id', 'unknown')
                    logger.info(f"[*] Attempting fallback: {provider_name} | {f_id}")
                    result = await agent.run(message, model=fallback_model)
                    evolution_logger.log_event(provider_name, f_id, "SUCCESS")
                    return result.data
                except Exception as ef:
                    logger.warning(f"[!] Fallback {provider_name} failed: {ef}")
                    evolution_logger.log_event(provider_name, "unknown", "FAILURE", error=str(ef))
                    continue
        
        # 3. Final Fallback: Local Gemini CLI
        try:
            logger.info("[*] Attempting final fallback with Local Gemini CLI...")
            response = await gemini_cli.generate_response(message)
            evolution_logger.log_event("local_cli", "gemini", "SUCCESS")
            return response
        except Exception as ecli:
            logger.error(f"[!] Local Gemini CLI failed: {ecli}")
            evolution_logger.log_event("local_cli", "gemini", "FAILURE", error=str(ecli))

        return "❌ **Ronaldinho fora de campo**: Todos os modelos (remotos e locais) falharam ou atingiram o limite. Por favor, verifique sua conexão ou chaves no .env!"
