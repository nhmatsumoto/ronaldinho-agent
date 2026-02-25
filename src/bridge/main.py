import asyncio
import os
import re
import httpx
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.error import BadRequest
from dotenv import load_dotenv

# Config Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ronaldinho-bridge")

# Load Env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NEURAL_CORE_URL = os.getenv("NEURAL_CORE_URL", "http://127.0.0.1:5000/api/chat")
BRIDGE_FILE = os.path.join(os.path.dirname(__file__), "../../.agent/brain/NEURAL_BRIDGE.md")
LAST_ID_FILE = os.path.join(os.path.dirname(__file__), "../../.agent/brain/LAST_TELEGRAM_ID.txt")

# Global Persistent Client for speed
http_client = httpx.AsyncClient(timeout=180)

async def send_large_message(bot, chat_id, text):
    """Splits a long message into chunks for Telegram with Markdown fallback."""
    MAX_LENGTH = 4000
    # Clean text to avoid some common markdown issues before sending
    # But let the fallback handle the heavy lifting
    chunks = [text[i:i+MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
    
    for chunk in chunks:
        if not chunk.strip(): continue
        try:
            # Try with Markdown first
            await bot.send_message(chat_id=chat_id, text=chunk, parse_mode="Markdown")
        except BadRequest as e:
            logger.warning(f"Markdown parse failed, falling back to plain text: {e}")
            # Explicit fallback for any parsing error
            try:
                await bot.send_message(chat_id=chat_id, text=chunk)
            except Exception as e2:
                logger.error(f"Failed to send plain text message: {e2}")
        except Exception as e:
            logger.error(f"Unexpected error in send_large_message: {e}")
            # Last ditch effort
            try:
                await bot.send_message(chat_id=chat_id, text=chunk)
            except: pass
        await asyncio.sleep(0.2)

async def check_neural_bridge(application):
    """Periodically checks the NEURAL_BRIDGE.md for Antigravity responses."""
    logger.info("[*] Neural Bridge Monitor Active.")
    processed_responses = set()
    
    while True:
        if os.path.exists(BRIDGE_FILE) and os.path.exists(LAST_ID_FILE):
            try:
                with open(LAST_ID_FILE, 'r') as f:
                    last_chat_id = f.read().strip()
                
                if last_chat_id:
                    with open(BRIDGE_FILE, 'r') as f:
                        content = f.read()
                    
                    responses = re.findall(r"--- \[RESPONSE TO: .*?\] ---\n(.*?)(?=\n--- \[|$)", content, re.DOTALL)
                    
                    for resp in responses:
                        resp_id = hash(resp.strip())
                        if resp_id not in processed_responses:
                            logger.info(f"[*] Found Antigravity response. Pushing to Telegram ID: {last_chat_id}")
                            header = "🛸 **MENSAGEM DO ANTIGRAVITY:**\n\n"
                            await send_large_message(application.bot, last_chat_id, header + resp.strip())
                            processed_responses.add(resp_id)
            except Exception as e:
                logger.error(f"[!] Error in Bridge Monitor: {e}")
        
        await asyncio.sleep(10)

async def typing_loop(context, chat_id, stop_event):
    """Keep the 'typing' indicator active until the response is ready."""
    while not stop_event.is_set():
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(4)
        except:
            break

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    chat_id = str(update.effective_chat.id)
    text = update.message.text
    
    # Save last chat ID for Antigravity fallbacks
    try:
        with open(LAST_ID_FILE, 'w') as f:
            f.write(chat_id)
    except: pass
    
    logger.info(f"[*] Mission received from {update.effective_user.first_name} ({user_id}): {text[:50]}...")
    
    # Start persistent typing indicator
    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(typing_loop(context, chat_id, stop_typing))
    
    try:
        response = await http_client.post(
            NEURAL_CORE_URL,
            json={"message": text, "user_id": user_id, "platform": "telegram"}
        )
        
        stop_typing.set()
        await typing_task
        
        if response.status_code == 200:
            reply = response.json().get("response", "Erro: Resposta vazia.")
            await send_large_message(context.bot, chat_id, reply)
        else:
            logger.error(f"Neural Core Error: {response.status_code}")
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Neural Core Busy ({response.status_code})")
            
    except Exception as e:
        stop_typing.set()
        logger.error(f"Connection error in handle_message: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Connection Lag or Error: {str(e)[:100]}")

async def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ ERROR: TELEGRAM_BOT_TOKEN not found!")
        return
        
    logger.info("🚀 Ronaldinho Python Bridge starting...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Start the monitor as a background task
    asyncio.create_task(check_neural_bridge(application))
    
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(message_handler)
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep running
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
