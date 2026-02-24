import google.generativeai as genai
from app.config import settings
import logging

logger = logging.getLogger("gemini-cli-local")

class LocalGeminiCLI:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Try to use a stable model ID
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    async def generate_response(self, prompt: str) -> str:
        if not self.model:
            return "❌ Local Gemini CLI: GEMINI_API_KEY não configurada."
        
        try:
            # Note: generate_content is synchronous in the basic SDK, 
            # but we wrap it for orchestrator compatibility
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in LocalGeminiCLI: {e}")
            return f"❌ Erro no Local Gemini CLI: {str(e)}"

# Singleton instance
gemini_cli = LocalGeminiCLI()
