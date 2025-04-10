from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

# Importiere alle Command Handler
from command_handlers import CommandHandlers
from message_handlers import MessageHandlers

##############################################
# MAIN: Bot-Setup und Polling
##############################################

class BotApp:
    def __init__(self, token: str):
        self.application = Application.builder().token(token).build()
        self.msg_handlers = MessageHandlers()
        self.cmd_handlers = CommandHandlers()
        self._configure_handlers()
        self._configure_jobs()

    def _configure_handlers(self):
        self.cmd_handlers.configure_conversation_handlers(self.application)
        self.application.add_handler(
            MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE, self.msg_handlers.handle_incoming_message)
        )

    def _configure_jobs(self):
        self.msg_handlers.configure_proactivity_jobs(self.application)

    def run(self):
        self.application.run_polling()




