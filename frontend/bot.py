import os
import logging
import datetime

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
from message_handlers import (
    send_morning_message,
    send_proactivity_message,
    handle_incoming_message
)

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
    #application.add_handler(CommandHandler("morning", send_morning_message))
    #application.add_handler(CommandHandler("proactivity", send_proactivity_message))

    application.job_queue.run_daily(
        send_morning_message,
        time=datetime.time(hour=21, minute=19, second=0), # 9 Uhr in DE-> 7 Uhr UTC
        name="morning_message"
    )

    application.job_queue.run_repeating(
        send_proactivity_message,
        interval=60,  # 3600 Sekunden = 1 Stunde
        first=0,        # Startet den Job sofort beim Hochfahren
        name="proactivity_message"
    )

    # Start polling
    application.run_polling()


if __name__ == "__main__":
    run_bot()

