from pydantic_ai import Agent, RunContext
from app.config import settings
from app.tools.terminal import TerminalTool
from app.tools.editor import EditorTool
import os

# Initialize Tools
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
terminal = TerminalTool(root_path)
editor = EditorTool(root_path)

# Map settings to Pydantic AI models
model_map = {
    "gemini": "google-gla:gemini-1.5-pro",
    "openai": "openai:gpt-4o",
    "anthropic": "anthropic:claude-3-5-sonnet-latest"
}
provider = settings.LLM_PROVIDER.lower()
model_id = model_map.get(provider, model_map["gemini"])

# Initialize Agent
agent = Agent(
    model_id,
    system_prompt=(
        "Você é o Ronaldinho, um agente autônomo baseado na Arquitetura Manus (Cloud).\n"
        "Sua operação baseia-se no Ciclo Real: Escreve -> Executa -> Lê -> Decide.\n\n"
        "1. **Escreve**: Quando precisar criar lógica complexa, escreva um arquivo Python real (.py).\n"
        "2. **Executa**: Rode o código ou comandos usando a ferramenta de terminal.\n"
        "3. **Lê**: Analise cuidadosamente o STDOUT e o STDERR retornados.\n"
        "4. **Decide**: Com base nos resultados, decida se o objetivo foi atingido ou se você precisa corrigir o código e repetir o ciclo.\n\n"
        "Você tem controle direto sobre o ambiente Linux. Seja fenomenal, proativo e use o feedback do terminal para se auto-corrigir."
    )
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
        result = await agent.run(message)
        return result.data
