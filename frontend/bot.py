import os
import logging
import datetime
import pytz

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
import api_client
import speech_utils

# Importiere alle Command Handler
from command_handlers import *

# Load environment variables
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

##############################################
# MESSAGE HANDLERS
##############################################

async def send_morning_message(context: ContextTypes.DEFAULT_TYPE):
    """Tägliche Morgenbotschaft über JobQueue senden."""
    chat_id = 8196289694 # sollte bekommen werden
    text = api_client.get_morning_message(chat_id)
    voice_output_path = speech_utils.generate_voice_message(text)
    await context.bot.send_message(chat_id=chat_id, text=text)
    await context.bot.send_voice(chat_id=chat_id, voice=open(voice_output_path, "rb"))

async def handle_incoming_message(update: Update, context: CallbackContext):
    """
    Handles both voice and text messages by sending replies in German.
    """

    if update.message.voice:
        voice_path = os.path.join(BASE_DIR, "output.ogg")
        voice_file = await update.message.voice.get_file()
        await voice_file.download_to_drive(voice_path)

        input_text = speech_utils.convert_voice_to_text(voice_path)
        text = api_client.get_answer(input_text, update.effective_user.id)
    else:
        text = api_client.get_answer(update.message.text, update.effective_user.id)

    voice_output_path = speech_utils.generate_voice_message(text)
    await update.message.reply_text(text)
    await update.message.reply_voice(voice=open(voice_output_path, "rb"))


##############################################
# MAIN: Bot-Setup und Polling
##############################################

def run_bot():
    """Main entry point für den Bot."""
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Konversationshandler für den Einrichtungsprozess (/start)
    init_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_initialization)],
        states={
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_course)],
            CAFETERIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_cafeteria)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_city)],
            TRANSPORT: [ CallbackQueryHandler(initialize_transport, pattern=r"^transport:")],
            STOCKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_stocks)],
            NEWS: [CallbackQueryHandler(initialize_news, pattern=r"^news:")],
        },
        fallbacks=[]
    )

    # Konversationshandler für das Ändern von Präferenzen (/changepref)
    update_handler = ConversationHandler(
        entry_points=[CommandHandler("changepref", start_change_preferences)],
        states={
            BUTTON: [CallbackQueryHandler(process_preference_button_click)],
            COURSE_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_course)],
            CAFETERIA_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_cafeteria)],
            CITY_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_city)],
            TRANSPORT_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_transport)],
            STOCKS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_stocks)],
            STOCKS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stocks)],
            NEWS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_news)],
            NEWS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_news)],
        },
        fallbacks=[]
    )

    application.add_handler(init_handler)
    application.add_handler(update_handler)
    application.add_handler(
        MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE, handle_incoming_message)
    )
    application.add_handler(CommandHandler("showpref", show_preferences))
    application.add_handler(CommandHandler("morning", send_morning_message))

    application.job_queue.run_daily(
        send_morning_message,
        time=datetime.time(hour=7, minute=0, second=0),
        name="morning_message"
    )

    # Start polling
    application.run_polling()


if __name__ == "__main__":
    run_bot()
    
