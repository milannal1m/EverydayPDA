from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

# Importiere alle Command Handler
from command_handlers import CommandHandlers
from message_handlers import (
    handle_incoming_message,
    configure_proactivity_jobs,
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
        cmd = CommandHandlers()
        cmd.configure_conversation_handlers(self.application)
        self.application.add_handler(
            MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE, handle_incoming_message)
        )

    def _configure_jobs(self):
        configure_proactivity_jobs(self.application)

    def run(self):
        self.application.run_polling()




