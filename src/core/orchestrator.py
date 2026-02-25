import os
import logging
import random
import asyncio
from pydantic_ai import Agent, RunContext

from config import settings
from tools.terminal import TerminalTool
from tools.editor import EditorTool
from tools.dev_toolkit import DevToolkit
from brain import detect_best_persona, get_integrated_system_prompt
from gemini_cli_local import gemini_cli
from evolution_logger import evolution_logger
from models import get_boot_model, get_model_instance, GEMINI_ROTATION_MODELS
from browser_model import browser_model
from skills_engine import skills_engine

logger = logging.getLogger("neural-core")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ExecutionLane:
    """
    Ensures serial execution per user/session.
    Prevents race conditions in tool usage (terminal, files).
    Inspired by OpenClaw's Lane Queue.
    """
    def __init__(self):
        self.locks = {}

    def get_lock(self, user_id: str) -> asyncio.Lock:
        if user_id not in self.locks:
            self.locks[user_id] = asyncio.Lock()
        return self.locks[user_id]

lane_manager = ExecutionLane()

# Global Tools Initialization
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
terminal = TerminalTool(root_path)
editor = EditorTool(root_path)
dev_toolkit = DevToolkit(root_path)

def create_agent(persona: str = None):
    """Creates a fresh PydanticAI Agent with the given persona."""
    system_prompt = get_integrated_system_prompt(root_path, active_persona=persona)
    
    agent = Agent(
        "google-gla:gemini-2.0-flash", # Base model
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

    @agent.tool
    def python_sandbox(ctx: RunContext[None], code: str) -> str:
        """Executa código Python isolado para testes rápidos."""
        return dev_toolkit.run_python_sandbox(code)

    @agent.tool
    def ask_antigravity(ctx: RunContext[None], question: str) -> str:
        """Envia uma pergunta complexa para o Orquestrador Central (Antigravity)."""
        bridge_path = os.path.join(root_path, ".agent/brain/NEURAL_BRIDGE.md")
        entry = f"\n\n--- [REQUEST AT {os.popen('date').read().strip()}] ---\n{question}\n"
        with open(bridge_path, 'a') as f:
            f.write(entry)
        return "Sua pergunta foi enviada ao Antigravity. Ele responderá na Ponte Neural em breve."
    
    @agent.tool
    def create_new_skill(ctx: RunContext[None], skill_name: str, description: str, python_code: str) -> str:
        """
        Cria uma nova habilidade (skill) permanentemente no sistema.
        OpenClaw Style: O agente expande suas próprias capacidades.
        """
        skill_dir = os.path.join(root_path, ".agent/skills", skill_name)
        os.makedirs(skill_dir, exist_ok=True)
        
        # Write SKILL.md
        with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
            f.write(f"#### Skill: {skill_name}\n{description}")
            
        # Write main.py
        with open(os.path.join(skill_dir, "main.py"), "w") as f:
            f.write(python_code)
            
        skills_engine.refresh_cache()
        return f"✅ Habilidade '{skill_name}' criada com sucesso e pronta para uso imediato (Engine Refreshed)."

    # --- Dynamic Skills Registration (OpenClaw Hub Style) ---
    dynamic_tools = skills_engine.discover_tools()
    for tool in dynamic_tools:
        agent.tool(tool)
        
    return agent

class Orchestrator:
    def __init__(self):
        self.current_persona = "default"
        self.active_agent = create_agent()
        logger.info("[🛸] Orchestrator initialized with OpenClaw Execution Engine.")

    async def process_message(self, message: str, user_id: str = "default_user") -> str:
        async with lane_manager.get_lock(user_id):
            return await self._process_logic(message)

    async def _process_logic(self, message: str) -> str:
        # 1. Persona Detection
        persona = detect_best_persona(message) or "default"
        if persona != self.current_persona:
            logger.info(f"[*] Switching to specialized persona: {persona}")
            self.active_agent = create_agent(persona if persona != "default" else None)
            self.current_persona = persona
        
        # 2. Strategy Choice: Complex Architecture vs Standard Task
        complexity_keywords = ["arquitetura", "refatore o core", "integracao complexa", "antigravity"]
        is_complex = any(kw in message.lower() for kw in complexity_keywords)
        
        # 3. Execution attempts (Prioritizing User Available Tools)
        # Sequence: Gemini API -> Ghost Browser (ChatGPT) -> Antigravity Bridge
        
        failures = []
        
        # --- PHASE 1: API GATEWAY (Multi-Provider) ---
        priority_providers = settings.MODEL_PRIORITY.split(",")
        
        for provider in priority_providers:
            # For Gemini, try rotation
            if provider == "gemini":
                for m_id in GEMINI_ROTATION_MODELS:
                    try:
                        model = get_model_instance("gemini", model_id=m_id)
                        if not model: continue
                        logger.debug(f"[*] Executing via {provider}:{m_id}")
                        result = await self.active_agent.run(message, model=model)
                        evolution_logger.log_event(provider, m_id, "SUCCESS")
                        return result.data
                    except Exception as e:
                        failures.append(f"{provider}:{m_id}: {str(e)[:40]}...")
            else:
                try:
                    model = get_model_instance(provider)
                    if not model: continue
                    logger.debug(f"[*] Executing via {provider}")
                    result = await self.active_agent.run(message, model=model)
                    evolution_logger.log_event(provider, "default", "SUCCESS")
                    return result.data
                except Exception as e:
                    failures.append(f"{provider}: {str(e)[:40]}...")
        
        # --- PHASE 2: BROWSER GHOST (ChatGPT) ---
        try:
            logger.info("[*] API levels depleted. Activating Browser Ghost Mode...")
            system_prompt = get_integrated_system_prompt(root_path, active_persona=persona)
            full_prompt = f"INSTRUCTIONS:\n{system_prompt}\n\nUSER MESSAGE:\n{message}"
            
            response = await browser_model.generate_response(full_prompt, service="chatgpt")
            if "Erro" not in response:
                evolution_logger.log_event("browser", "chatgpt", "SUCCESS")
                return response
            failures.append(f"Browser: {response[:50]}...")
        except Exception as e:
            logger.error(f"[!] Browser Ghost Mode failed: {e}")
            failures.append(f"Browser: {str(e)[:50]}...")

        # --- PHASE 3: NEURAL BRIDGE (Final Handoff) ---
        logger.info("[*] All local autonomous models failed. Handing off to Antigravity Bridge.")
        bridge_msg = (
            f"❌ **Ronaldinho em modo de espera**: As APIs e o Browser não conseguiram processar sua mensagem.\n\n"
            f"**Histórico de Falhas:**\n- " + "\n- ".join(failures) + "\n\n"
            f"🚀 **Ação Tomada:** Enviei sua solicitação automaticamente para a **Ponte Neural do Antigravity**. "
            f"Ele analisará o contexto e fornecerá a resposta diretamente em `.agent/brain/NEURAL_BRIDGE.md`."
        )
        
        # Auto-write to bridge
        try:
            bridge_path = os.path.join(root_path, ".agent/brain/NEURAL_BRIDGE.md")
            entry = f"\n\n--- [AUTO-FALLBACK AT {os.popen('date').read().strip()}] ---\nUSER: {message}\nFAILURES: {failures}\n"
            with open(bridge_path, 'a') as f:
                f.write(entry)
        except: pass
        
        return bridge_msg
