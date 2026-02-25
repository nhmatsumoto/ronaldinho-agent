import asyncio
import os
import logging
import json
import httpx
from playwright.async_api import async_playwright

logger = logging.getLogger("browser-model")

class BrowserModel:
    def __init__(self, session_dir: str):
        self.session_dir = session_dir
        self.browser_context = None
        self.playwright = None
        self.access_token = None
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    async def _setup(self, headless=True):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser_context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.session_dir,
                headless=headless,
                user_agent=self.user_agent,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--window-size=1920,1080"
                ]
            )
            page = self.browser_context.pages[0] if self.browser_context.pages else await self.browser_context.new_page()
            
            # Listen for session data to extract the Access Token automatically
            page.on("response", self._intercept_auth)
            
            await page.set_viewport_size({"width": 1920, "height": 1080})
            return page
        return self.browser_context.pages[0]

    async def _intercept_auth(self, response):
        """Intercepts internal auth session to get the Access Token."""
        # logger.debug(f"Intercepted: {response.url}")
        if "auth/session" in response.url and response.status == 200:
            try:
                data = await response.json()
                if "accessToken" in data:
                    self.access_token = data["accessToken"]
                    logger.info("[*] ChatGPT Access Token Intercepted Successfully!")
                    # Save it for light persistence
                    with open(os.path.join(self.session_dir, "last_token.txt"), "w") as f:
                        f.write(self.access_token)
                else:
                    logger.warning(f"[!] Auth session found but no accessToken in response: {list(data.keys())}")
            except Exception as e:
                logger.debug(f"Failed to parse auth session JSON: {e}")

    async def generate_response(self, prompt: str, service="chatgpt") -> str:
        """
        Generates response. 
        Tries Autonomous API first (Direct HTTP), then falls back to Browser Ghosting.
        """
        # Load token if exists
        token_path = os.path.join(self.session_dir, "last_token.txt")
        if not self.access_token and os.path.exists(token_path):
            with open(token_path, "r") as f:
                self.access_token = f.read().strip()

        # 1. ATTEMPT AUTONOMOUS API MODE (Dribbling Cloudflare)
        if self.access_token:
            try:
                # This is a simplified version of the unofficial API logic
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json",
                        "User-Agent": self.user_agent,
                        "Accept": "text/event-stream"
                    }
                    payload = {
                        "action": "next",
                        "messages": [{
                            "id": "cb1c876e-821f-11ed-a1eb-0242ac120002",
                            "author": {"role": "user"},
                            "content": {"content_type": "text", "parts": [prompt]},
                            "metadata": {}
                        }],
                        "model": "auto",
                        "parent_message_id": "cb1c876e-821f-11ed-a1eb-0242ac120002", # Simplified
                        "timezone_offset_min": -180,
                        "history_and_training_disabled": False
                    }
                    
                    # Note: Direct backend-api often needs more complex cookies/headers
                    # We try it, but fall back instantly if it fails
                    resp = await client.post("https://chatgpt.com/backend-api/conversation", 
                                          json=payload, headers=headers, timeout=20)
                    if resp.status_code == 200:
                        logger.info("[*] Autonomous Engine: Direct API success.")
                        # Parse SSE response (simplified)
                        lines = resp.text.split("\n")
                        last_data = ""
                        for line in lines:
                            if line.startswith("data: "):
                                try:
                                    data_part = json.loads(line[6:])
                                    if "message" in data_part and "content" in data_part["message"]:
                                        last_data = "".join(data_part["message"]["content"]["parts"])
                                except: pass
                        if last_data: return last_data
            except Exception as e:
                logger.debug(f"Direct API failed, falling back to browser: {e}")

        # 2. FALLBACK TO BROWSER GHOST MODE (Playwright)
        page = await self._setup(headless=True)
        try:
            if service == "chatgpt":
                await page.goto("https://chatgpt.com", wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(8)
                
                if await page.query_selector("text=Log in") or await page.query_selector("text=Sign in"):
                    return "❌ Erro: Sessão expirada. Rode './scripts/browser_login.sh' no painel."

                # Find input
                selectors = ["#prompt-textarea", "textarea", "div[contenteditable='true']"]
                input_field = None
                for _ in range(10):
                    for s in selectors:
                        input_field = await page.query_selector(s)
                        if input_field: break
                    if input_field: break
                    await asyncio.sleep(1)
                
                if not input_field: return "❌ Erro: ChatGPT UI não carregou ou campo não encontrado."

                await input_field.fill(prompt)
                await asyncio.sleep(1)
                await page.keyboard.press("Enter")
                
                # Wait respond
                await asyncio.sleep(8)
                try:
                    await page.wait_for_selector("button[data-testid='send-button']:not([disabled])", timeout=120000)
                except: pass
                
                messages = await page.query_selector_all("div[data-message-author-role='assistant']")
                if messages:
                    return await messages[-1].inner_text()
                
                return "❌ Erro: Resposta não detectada."
        except Exception as e:
            return f"❌ Erro Crítico BrowserModel: {str(e)}"

    async def close(self):
        if self.browser_context: await self.browser_context.close()
        if self.playwright: await self.playwright.stop()

# Singleton
session_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/browser_session"))
browser_model = BrowserModel(session_path)
