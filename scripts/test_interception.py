import asyncio
import os
import sys

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add src/core to path
sys.path.append(os.path.abspath("src/core"))

from browser_model import browser_model

async def main():
    print("[*] Iniciando motor autonomo para interceptação de token...")
    # This will trigger the _setup and the _intercept_auth listener
    response = await browser_model.generate_response("Diga 'Conexão Estabelecida' se puder me ouvir.", service="chatgpt")
    
    print(f"[*] Resposta do ChatGPT: {response}")
    
    token_path = os.path.join(browser_model.session_dir, "last_token.txt")
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            token = f.read().strip()
            print(f"✅ SUCESSO! Token capturado: {token[:20]}...")
    else:
        print("❌ FALHA: O token não foi interceptado. Verifique se o login foi feito corretamente.")
    
    await browser_model.close()

if __name__ == "__main__":
    asyncio.run(main())
