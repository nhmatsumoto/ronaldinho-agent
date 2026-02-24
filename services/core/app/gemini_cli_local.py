import subprocess
import json
import logging
import shutil
import asyncio
import os
from app.config import settings

logger = logging.getLogger("gemini-cli-local")

class LocalGeminiCLI:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.executable = shutil.which("gemini")
        logger.info(f"[*] LocalGeminiCLI initialized. Global 'gemini' executable: {self.executable}")
        
    async def generate_response(self, prompt: str) -> str:
        """
        Gera uma resposta usando o ferramenta gemini-cli via subprocess.
        Tenta usar o comando 'gemini' global se disponível, caso contrário usa 'npx'.
        """
        cmd = []
        if self.executable:
            cmd = [self.executable]
        else:
            # Fallback to npx if global gemini is not found
            cmd = ["npx", "-y", "@google/gemini-cli"]

        import shlex
        # Arguments for non-interactive execution with JSON output
        # -p: prompt
        # --output-format json: returns structured response
        full_cmd_str = " ".join(cmd + ["-p", shlex.quote(prompt), "--output-format", "json"])
        
        env = os.environ.copy()
        if self.api_key:
            env["GEMINI_API_KEY"] = self.api_key

        try:
            logger.info(f"[*] Executing Local Gemini CLI: {full_cmd_str}")
            process = await asyncio.create_subprocess_shell(
                full_cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            # npm/node often emit warnings to stderr even on success.
            # We only treat it as a failure if returncode is non-zero.
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"Local Gemini CLI failed (code {process.returncode}): {error_msg}")
                raise Exception(f"Local Gemini CLI error: {error_msg}")

            output = stdout.decode().strip()
            if not output:
                return "❌ Erro no Fallback Local: Saída vazia do CLI."

            try:
                # The CLI returns a JSON object including the text in the 'response' field
                data = json.loads(output)
                if isinstance(data, dict) and "response" in data:
                    return data["response"]
                
                # Fallback extraction if structure changed
                if isinstance(data, dict):
                    if "text" in data: return data["text"]
                    if "candidates" in data: return data["candidates"][0]["content"]["parts"][0]["text"]
                
                return str(data)
            except json.JSONDecodeError:
                # If it's not JSON, it might be the raw text (if --output-format json failed or wasn't used)
                return output

        except Exception as e:
            logger.error(f"Error in LocalGeminiCLI: {e}")
            return f"❌ Erro no Fallback Local: {str(e)}"

# Singleton instance
gemini_cli = LocalGeminiCLI()
