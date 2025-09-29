from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os, requests
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Ton token Telegram
HF_API_KEY = os.getenv("HF_API_KEY")                 # Ton Hugging Face token

app = FastAPI()

# Initialiser le bot Telegram
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Fonction pour interroger Hugging Face
def query_huggingface(prompt: str):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {"inputs": prompt}
    response = requests.post(
        "https://api-inference.huggingface.co/models/gpt2",
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        try:
            return response.json()[0]["generated_text"]
        except Exception:
            return str(response.json())
    else:
        return f"❌ Erreur Hugging Face API: {response.status_code}"

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello 👋, je suis ton bot avec Hugging Face LLM !")

# Répondre aux messages avec Hugging Face
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = query_huggingface(user_text)
    await update.message.reply_text(response)

# Ajouter handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Endpoint webhook
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"ok": True}