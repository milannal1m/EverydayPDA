import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
import api_handler
from dotenv import load_dotenv


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
print(TELEGRAM_API_KEY)

# Logging einrichten
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Start-Befehl
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hallo! Ich bin dein Telegram-Bot.")

# Echo-Handler
async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(api_handler.get_answer(update.message.text)["answer"])

# Hauptfunktion
def main():
    # Telegram Bot-Token
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Befehle und Nachrichtenhandler hinzufügen
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Startet den Bot
    application.run_polling()

if __name__ == "__main__":
    main()
