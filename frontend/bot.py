import datetime


from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

# Importiere alle Command Handler
from command_handlers import configure_conversation_handlers
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
        configure_conversation_handlers(self.application)
        self.application.add_handler(
            MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE, handle_incoming_message)
        )

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




