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
    
    return agent

class Orchestrator:
    def __init__(self):
        self.active_agent = create_agent()

    async def process_message(self, message: str) -> str:
        # 1. Persona Detection
        persona = detect_best_persona(message)
        if persona:
            logger.info(f"[*] Switching to specialized persona: {persona}")
            self.active_agent = create_agent(persona)
        
        # 2. Strategy Choice: Complex Architecture vs Standard Task
        complexity_keywords = ["arquitetura", "refatore o core", "integracao complexa", "antigravity"]
        is_complex = any(kw in message.lower() for kw in complexity_keywords)
        
        # 3. Execution attempts (Prioritizing User Available Tools)
        # Sequence: Gemini API -> Ghost Browser (ChatGPT) -> Antigravity Bridge
        
        failures = []
        
        # --- PHASE 1: GEMINI API ---
        for m_id in GEMINI_ROTATION_MODELS:
            try:
                model = get_model_instance("gemini", model_id=m_id)
                if not model: continue
                
                logger.debug(f"[*] Attempting Gemini API: {m_id}")
                result = await self.active_agent.run(message, model=model)
                evolution_logger.log_event("gemini", m_id, "SUCCESS")
                return result.data
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                    logger.warning(f"[!] Gemini {m_id} quota exceeded.")
                else:
                    logger.warning(f"[!] Gemini {m_id} failed: {err_str[:100]}")
                failures.append(f"Gemini {m_id}: {err_str[:50]}...")
                continue
        
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
