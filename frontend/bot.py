import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Logging einrichten
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Start-Befehl
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hallo! Ich bin dein Telegram-Bot.")

# Echo-Handler
async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

# Hauptfunktion
def main():
    # Ersetze 'DEIN_TOKEN' mit deinem echten Bot-Token
    application = Application.builder().token("7129624717:AAG9Hwft0x0YX20YAm3Pz0F9thLRuKq3vUU").build()

    # Befehle und Nachrichtenhandler hinzufügen
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Startet den Bot
    application.run_polling()

if __name__ == "__main__":
    main()
