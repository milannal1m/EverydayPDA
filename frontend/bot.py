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

# Importiere alle Command Handler
from command_handlers import (
    start_initialization,
    initialize_course,
    initialize_cafeteria,
    initialize_city,
    initialize_transport,
    initialize_stocks,
    initialize_news,
    start_change_preferences,
    process_preference_button_click,
    change_course,
    change_cafeteria,
    change_city,
    change_transport,
    remove_stocks,
    add_stocks,
    remove_news,
    add_news,
    show_preferences,
    COURSE,
    CAFETERIA,
    CITY,
    TRANSPORT,
    STOCKS,
    NEWS,
    BUTTON,
    COURSE_UPDATE,
    CAFETERIA_UPDATE,
    CITY_UPDATE,
    TRANSPORT_UPDATE,
    STOCKS_DELETE,
    STOCKS_ADD,
    NEWS_DELETE,
    NEWS_ADD,
    BUTTON
)
from message_handlers import (
    send_morning_message,
    send_proactivity_message,
    handle_incoming_message
)

##############################################
# MAIN: Bot-Setup und Polling
##############################################

class BotApp:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self._configure_handlers()
        self._configure_jobs()

    def _configure_handlers(self):
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
        self.application.add_handler(init_handler)
        self.application.add_handler(update_handler)
        self.application.add_handler(
            MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE, handle_incoming_message)
        )
        self.application.add_handler(CommandHandler("showpref", show_preferences))

    def _configure_jobs(self):
        self.application.job_queue.run_daily(
            send_morning_message,
            time=datetime.time(hour=21, minute=19, second=0),
            name="morning_message"
        )
        self.application.job_queue.run_repeating(
            send_proactivity_message,
            interval=60,
            first=0,
            name="proactivity_message"
        )

    def run(self):
        self.application.run_polling()




