import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import httpx
from dotenv import load_dotenv

# Load Env
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NEURAL_CORE_URL = os.getenv("NEURAL_CORE_URL", "http://localhost:5000/api/chat")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    print(f"[*] Message from {user_id}: {text}")
    
    # Send to Neural Core
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                NEURAL_CORE_URL,
                json={"message": text, "user_id": user_id, "platform": "telegram"},
                timeout=60
            )
            if response.status_code == 200:
                reply = response.json().get("response", "Erro: Resposta vazia.")
                await update.message.reply_text(reply)
            else:
                await update.message.reply_text(f"Erro no Neural Core: {response.status_code}")
        except Exception as e:
            await update.message.reply_text(f"Erro de conexão: {str(e)}")

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found!")
        exit(1)
        
    print("🚀 Ronaldinho Python Bridge starting...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(message_handler)
    
    application.run_polling()
