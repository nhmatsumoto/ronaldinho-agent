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
        self.user_pages = {} # Map user_id to page
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    async def _setup(self, user_id="default_user", headless=True):
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
                    "--window-size=1280,720"
                ]
            )
        
        if user_id not in self.user_pages or self.user_pages[user_id].is_closed():
            page = await self.browser_context.new_page()
            page.on("response", self._intercept_auth)
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            # Initial load to chatgpt
            try:
                await page.goto("https://chatgpt.com", wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(2)
            except: pass
            
            self.user_pages[user_id] = page

        return self.user_pages[user_id]

    async def _extract_token_via_js(self, page):
        try:
            token = await page.evaluate("() => { try { return JSON.stringify(window.__NEXT_DATA__.props.pageProps.session); } catch(e) { return null; } }")
            if token:
                data = json.loads(token)
                acc_token = data.get("accessToken")
                if acc_token:
                    self._save_token(acc_token)
                    return
            
            acc_token = await page.evaluate("async () => { try { const r = await fetch('/api/auth/session'); const d = await r.json(); return d.accessToken; } catch(e) { return null; } }")
            if acc_token:
                self._save_token(acc_token)
        except Exception as e:
            logger.debug(f"JS Token Extraction failed: {e}")

    def _save_token(self, token):
        self.access_token = token
        logger.info("[*] ChatGPT Token Intercepted/Extracted Successfully!")
        token_path = os.path.join(self.session_dir, "last_token.txt")
        with open(token_path, "w") as f:
            f.write(self.access_token)

    async def _intercept_auth(self, response):
        url = response.url.lower()
        if "auth/session" in url and response.status == 200:
            try:
                data = await response.json()
                if "accessToken" in data:
                    self._save_token(data["accessToken"])
            except: pass

    async def generate_response(self, prompt: str, service="chatgpt", user_id="default_user") -> str:
        try:
            return await asyncio.wait_for(self._generate_logic(prompt, service, user_id), timeout=95)
        except asyncio.TimeoutError:
            return "❌ Erro: Timeout (95s). O ChatGPT está demorando muito para responder."
        except Exception as e:
            logger.error(f"[!] Browser failure: {e}")
            return f"❌ Erro Crítico Motor: {str(e)}"

    async def _generate_logic(self, prompt: str, service="chatgpt", user_id="default_user") -> str:
        token_path = os.path.join(self.session_dir, "last_token.txt")
        if not self.access_token and os.path.exists(token_path):
            with open(token_path, "r") as f:
                self.access_token = f.read().strip()

        # 1. AUTONOMOUS API MODE
        if self.access_token:
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json",
                        "User-Agent": self.user_agent
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
                        "parent_message_id": "cb1c876e-821f-11ed-a1eb-0242ac120002",
                        "timezone_offset_min": -180,
                        "history_and_training_disabled": False
                    }
                    resp = await client.post("https://chatgpt.com/backend-api/conversation", 
                                          json=payload, headers=headers, timeout=30)
                    if resp.status_code == 200:
                        last_data = ""
                        for line in resp.text.split("\n"):
                            if line.startswith("data: "):
                                try:
                                    data_part = json.loads(line[6:])
                                    if "message" in data_part and "content" in data_part["message"]:
                                        last_data = "".join(data_part["message"]["content"]["parts"])
                                except: pass
                        if last_data: return last_data
            except: pass

        # 2. BROWSER GHOST MODE (Playwright)
        page = await self._setup(user_id=user_id, headless=True)
        try:
            if service == "chatgpt":
                # Only goto if we are not already on chatgpt
                if "chatgpt.com" not in page.url:
                    await page.goto("https://chatgpt.com", wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(3)
                
                if await page.query_selector("text=Log in") or await page.query_selector("text=Sign in"):
                    return "❌ Erro: Login necessário no ChatGPT."

                selectors = ["#prompt-textarea", "textarea", "div[contenteditable='true']"]
                input_field = None
                for _ in range(10):
                    for s in selectors:
                        input_field = await page.query_selector(s)
                        if input_field: break
                    if input_field: break
                    await asyncio.sleep(1)
                
                if not input_field: return "❌ Erro: Campo de entrada não encontrado."

                await input_field.fill(prompt)
                await asyncio.sleep(1)
                await page.keyboard.press("Enter")
                
                await asyncio.sleep(10)
                try:
                    await page.wait_for_selector("button[data-testid='send-button']:not([disabled])", timeout=120000)
                except: pass
                
                messages = await page.query_selector_all("div[data-message-author-role='assistant']")
                if messages: return await messages[-1].inner_text()
                
                return "❌ Erro: Resposta não detectada."
        except Exception as e:
            return f"❌ Erro Browser: {str(e)}"
        return "❌ Erro Desconhecido."

    async def close(self):
        if self.browser_context: await self.browser_context.close()
        if self.playwright: await self.playwright.stop()

# Singleton
session_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.agent/browser_session"))
browser_model = BrowserModel(session_path)
