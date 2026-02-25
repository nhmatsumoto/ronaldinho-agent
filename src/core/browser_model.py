import asyncio
import os
import logging
from playwright.async_api import async_playwright
from playwright_stealth import stealth

logger = logging.getLogger("browser-model")

class BrowserModel:
    def __init__(self, session_dir: str):
        self.session_dir = session_dir
        self.browser_context = None
        self.playwright = None

    async def _setup(self, headless=True):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser_context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.session_dir,
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            # Apply stealth to all pages in the context
            page = self.browser_context.pages[0] if self.browser_context.pages else await self.browser_context.new_page()
            await stealth(page)
            return page
        return self.browser_context.pages[0]

    async def generate_response(self, prompt: str, service="chatgpt") -> str:
        """
        Uses a browser to interact with an AI chat service.
        Currently supports: chatgpt
        """
        page = await self._setup(headless=True)
        
        try:
            if service == "chatgpt":
                await page.goto("https://chatgpt.com", wait_until="networkidle")
                
                # Check if we need to login (basic check)
                if await page.query_selector("text=Log in"):
                    return "❌ Erro no BrowserModel: Necessário fazer login no ChatGPT. Execute o script de login."

                # Find the prompt textarea
                # Multiple possible selectors for ChatGPT's input
                selectors = ["#prompt-textarea", "textarea", "div[contenteditable='true']"]
                input_field = None
                for selector in selectors:
                    input_field = await page.query_selector(selector)
                    if input_field:
                        break
                
                if not input_field:
                    return "❌ Erro no BrowserModel: Não foi possível encontrar o campo de input do ChatGPT."

                await input_field.fill(prompt)
                await page.keyboard.press("Enter")

                # Wait for the response to start and finish
                # ChatGPT usually has a 'stop generating' button or similar while responding
                await asyncio.sleep(2) # Wait for initial start
                
                # Wait for the "Send message" button to reappear (means finishing)
                # or wait for the "Stop generating" button to disappear
                await page.wait_for_selector("button[data-testid='send-button']:not([disabled])", timeout=120000)
                
                # Get the last assistant message
                # ChatGPT uses articles or divs for messages
                messages = await page.query_selector_all("div[data-message-author-role='assistant']")
                if messages:
                    last_message = messages[-1]
                    return await last_message.inner_text()
                
                return "❌ Erro no BrowserModel: Resposta não encontrada."

            else:
                return f"❌ Erro no BrowserModel: Serviço '{service}' não suportado ainda."

        except Exception as e:
            logger.error(f"BrowserModel Error: {e}")
            return f"❌ Erro no BrowserModel: {str(e)}"
        finally:
            # We keep the context open for performance, or we could close it.
            # For now, let's keep it open.
            pass

    async def close(self):
        if self.browser_context:
            await self.browser_context.close()
        if self.playwright:
            await self.playwright.stop()

# Singleton instance
session_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/browser_session"))
browser_model = BrowserModel(session_path)
