import os
import logging
import random
import asyncio
from pydantic_ai import Agent, RunContext

from config import settings
from tools.terminal import TerminalTool
from tools.editor import EditorTool
from tools.dev_toolkit import DevToolkit
from brain import get_integrated_system_prompt, detect_best_persona
from benchmarker import get_latencies, get_fastest_provider
from gemini_cli_local import gemini_cli
from evolution_logger import evolution_logger
from models import get_boot_model, get_model_instance, GEMINI_ROTATION_MODELS
from browser_model import browser_model

logger = logging.getLogger("neural-core")

# Global Tools Initialization
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
terminal = TerminalTool(root_path)
editor = EditorTool(root_path)
dev_toolkit = DevToolkit(root_path)

def create_agent(persona: str = None):
    """Creates a fresh PydanticAI Agent with the given persona."""
    system_prompt = get_integrated_system_prompt(root_path, active_persona=persona)
    
    agent = Agent(
        "google-gla:gemini-2.0-flash", # Default, can be overridden in run()
        system_prompt=system_prompt
    )

    # Register Tools
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

    # Dev Mastery Tools
    @agent.tool
    def git_ops(ctx: RunContext[None], action: str, message: str = None) -> str:
        """Gerencia o repositório GIT (status, commit). Action: 'status' ou 'commit'."""
        if action == "status": return dev_toolkit.get_git_status()
        if action == "commit": return dev_toolkit.git_commit(message or "chore: auto update")
        return "Ação inválida."

    @agent.tool
    def python_sandbox(ctx: RunContext[None], code: str) -> str:
        """Executa código Python isolado para testes rápidos."""
        return dev_toolkit.run_python_sandbox(code)
    
    return agent

class Orchestrator:
    def __init__(self):
        self.active_agent = create_agent()

    async def get_dynamic_model(self, is_coding_task: bool = False):
        if is_coding_task and settings.NVIDIA_API_KEY:
            instance = get_model_instance("nvidia", model_id="meta/llama-3.1-405b-instruct")
            if instance: return instance
            
        if settings.ENABLE_BENCHMARKING:
            try:
                latencies = await get_latencies()
                fastest = get_fastest_provider(latencies)
                instance = get_model_instance(fastest)
                if instance: return instance
            except Exception: pass

        return get_boot_model()

    async def process_message(self, message: str) -> str:
        # 1. Detect Intent and Persona
        persona = detect_best_persona(message)
        if persona:
            logger.info(f"[*] Switching to specialized persona: {persona}")
            self.active_agent = create_agent(persona)
        
        coding_keywords = ["escreva", "refatore", "bug", "fix", "python", "code", "docker", "implemente"]
        is_coding = any(kw in message.lower() for kw in coding_keywords)
        
        # 2. Try Primary Model
        try:
            model = await self.get_dynamic_model(is_coding_task=is_coding)
            if model:
                try:
                    logger.info(f"[*] Running with primary model: {model}")
                    result = await self.active_agent.run(message, model=model)
                    evolution_logger.log_event("dynamic", str(model), "SUCCESS")
                    return result.data
                except Exception as e:
                    logger.warning(f"[!] Primary model failed: {e}. Starting rotation...")
        except Exception as e:
            logger.error(f"[!] Dynamic model acquisition failed: {e}")

        # 3. Rotation Logic
        priority = settings.MODEL_PRIORITY.split(",")
        failures = []
        for provider in priority:
            candidates = [None] if provider != "gemini" else GEMINI_ROTATION_MODELS
            for m_id in candidates:
                try:
                    fallback_model = get_model_instance(provider, model_id=m_id)
                    if not fallback_model: continue
                    
                    logger.info(f"[*] Attempting fallback: {provider} | {m_id or 'default'}")
                    result = await self.active_agent.run(message, model=fallback_model)
                    evolution_logger.log_event(provider, m_id or "default", "SUCCESS")
                    return result.data
                except Exception as ef:
                    failures.append(f"{provider}: {str(ef)[:50]}...")
                    logger.warning(f"[!] Fallback {provider} failed: {ef}")
                    continue
        
        # 4. Fallback: Local CLI (often has independent daily quota)
        try:
            logger.info("[*] Remote models failed. Using local CLI fallback.")
            cli_response = await gemini_cli.generate_response(message)
            if "quota" in cli_response.lower() or "error" in cli_response.lower():
                 raise Exception(cli_response)
            return cli_response
        except Exception as e:
            logger.warning(f"[!] Local CLI failed: {e}. Activating Ghost Browser Fallback...")
        
        # 5. Final Fallback: Browser Ghost (ChatGPT Web)
        try:
            logger.info("[*] Activating final ghost fallback: Browser ChatGPT")
            # We inject the system prompt into the browser message to maintain context
            system_prompt = get_integrated_system_prompt(root_path, active_persona=persona)
            full_prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER MESSAGE:\n{message}"
            
            response = await browser_model.generate_response(full_prompt, service="chatgpt")
            return response
        except Exception as e:
            logger.error(f"Critical failure: {e}")
            failure_summary = "\n- ".join(failures)
            return (
                f"❌ **Ronaldinho fora de campo**: Todos os modelos, o CLI local e o Browser falharam.\n\n"
                f"**Motivos:**\n- {failure_summary}\n\n"
                f"💡 **Dica:** Parece que suas cotas gratuitas acabaram e o browser não está logado. "
                f"Tente adicionar uma chave da Groq ou execute `scripts/browser_login.sh` para autenticar no ChatGPT!"
            )
