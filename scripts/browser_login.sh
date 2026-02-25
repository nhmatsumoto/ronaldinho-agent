#!/bin/bash

# Ronaldinho Agent: Browser Login Helper
# Use this to log in to services like ChatGPT, Claude, etc.
# Your session will be saved in .agent/browser_session/

echo "🏀 Ronaldinho Browser Login Helper"
echo "[*] Preparando navegador para login manual..."

# Clear Playwright locks for Chromium to prevent ProcessSingleton errors
session_dir=$(pwd)/.agent/browser_session
find "$session_dir" -name "SingletonLock" -delete 2>/dev/null
find "$session_dir" -name "SingletonSocket" -delete 2>/dev/null
find "$session_dir" -name "SingletonCookie" -delete 2>/dev/null

PYTHON_BIN=$(pwd)/venv/bin/python3

$PYTHON_BIN -c "
import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    session_dir = os.path.abspath('.agent/browser_session')
    async with async_playwright() as p:
        print(f'[*] Abrindo navegador em: {session_dir}')
        context = await p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        print('\n🚀 LOGIN MANUAL NECESSÁRIO:')
        print('1. Acesse o site desejado (ex: https://chatgpt.com)')
        print('2. Faça o login normalmente.')
        print('3. Quando terminar, FECHE O NAVEGADOR para salvar a sessão.\n')
        
        await page.goto('https://chatgpt.com')
        
        # Keep it open until the browser is closed manually
        while True:
            try:
                if context.pages:
                    await asyncio.sleep(1)
                else:
                    break
            except Exception:
                break
        
        print('[*] Sessão salva com sucesso!')

asyncio.run(run())
"

echo "[!] Ronaldinho: Sessão de navegador atualizada."
