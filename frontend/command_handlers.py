import logging
from telegram.ext import (
    Application, ConversationHandler, CommandHandler, 
    MessageHandler, CallbackQueryHandler, filters
)

from pref_config import *
from start_handler import StartHandler
from pref_handler import PreferenceHandler

logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self):
        self.start_handler = StartHandler()
        self.pref_handler = PreferenceHandler()

    def configure_conversation_handlers(self, application: Application):
        """Registriert alle ConversationHandler und Commands in der Application."""
        init_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start_handler.start_initialization)],
            states={
                COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.start_handler.initialize_course)],
                CAFETERIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.start_handler.initialize_cafeteria)],
                CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.start_handler.initialize_city)],
                TRANSPORT: [CallbackQueryHandler(self.start_handler.initialize_transport, pattern=r"^transport:")],
                STOCKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.start_handler.initialize_stocks)],
                NEWS: [CallbackQueryHandler(self.start_handler.initialize_news, pattern=r"^news:")],
            },
            fallbacks=[]
        )

        update_handler = ConversationHandler(
            entry_points=[CommandHandler("changepref", self.pref_handler.start_change_preferences)],
            states={
                BUTTON: [CallbackQueryHandler(self.pref_handler.process_preference_button_click)],
                COURSE_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.change_course)],
                CAFETERIA_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.change_cafeteria)],
                CITY_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.change_city)],
                TRANSPORT_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.change_transport)],
                STOCKS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.remove_stocks)],
                STOCKS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.add_stocks)],
                NEWS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.remove_news)],
                NEWS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pref_handler.add_news)],
            },
            fallbacks=[]
        )

        # ConversationHandler in der Application registrieren
        application.add_handler(init_handler)
        application.add_handler(update_handler)
        application.add_handler(CommandHandler("showpref", self.pref_handler.show_preferences))
