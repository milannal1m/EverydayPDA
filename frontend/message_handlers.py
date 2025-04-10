import os
import logging
import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CallbackContext,
    Application
)

import speech_utils
import api_client

class MessageHandlers:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Du kannst BASE_DIR auch im Konstruktor definieren:
        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    async def send_morning_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Tägliche Morgenbotschaft über JobQueue senden."""
        response = api_client.get_all_morning_messages()

        if isinstance(response, str):
            self.logger.warning(f"Fehler beim Abrufen der Morgenmeldungen: {response}")
            return

        for item in response:
            text = item["response"]
            user_id = item["user_id"]

            if text is None:
                self.logger.warning(f"Keine Morgenmeldung für Benutzer {user_id} gefunden.")
                continue

            voice_output_path = speech_utils.generate_voice_message(text)
            await context.bot.send_message(chat_id=user_id, text=text)
            await context.bot.send_voice(chat_id=user_id, voice=open(voice_output_path, "rb"))

    async def send_proactivity_message(self, context: ContextTypes.DEFAULT_TYPE):
        """Tägliche Proaktivitätsnachricht über JobQueue senden."""
        response = api_client.get_all_proactivity_messages()

        if isinstance(response, str):
            self.logger.warning(f"Fehler beim Abrufen der Proaktivitätsmeldungen: {response}")
            return

        for item in response:
            text = item["response"]
            user_id = item["user_id"]

            if text is None:
                self.logger.warning(f"Keine Proaktivitätsmeldung für Benutzer {user_id} gefunden.")
                continue

            voice_output_path = speech_utils.generate_voice_message(text)
            await context.bot.send_message(chat_id=user_id, text=text)
            await context.bot.send_voice(chat_id=user_id, voice=open(voice_output_path, "rb"))

    async def handle_incoming_message(self, update: Update, context: CallbackContext):
        """Verarbeitet Sprach- und Textnachrichten und gibt eine Antwort zurück."""
        if update.message.voice:
            voice_path = os.path.join(self.BASE_DIR, "output.ogg")
            voice_file = await update.message.voice.get_file()
            await voice_file.download_to_drive(voice_path)

            input_text = speech_utils.convert_voice_to_text(voice_path)
            text = api_client.get_answer(input_text, update.effective_user.id)
        else:
            text = api_client.get_answer(update.message.text, update.effective_user.id)

        voice_output_path = speech_utils.generate_voice_message(text)
        await update.message.reply_text(text)
        await update.message.reply_voice(voice=open(voice_output_path, "rb"))

    def configure_proactivity_jobs(self, application: Application):
        """Richtet die regelmäßigen Jobs für Morgen- und Proaktivitätsnachrichten ein."""
        morning_time = datetime.time(hour=21, minute=19, second=0)
        proactivity_interval = 600  # Sekunden

        application.job_queue.run_daily(
            self.send_morning_message,
            time=morning_time,
            name="morning_message"
        )
        application.job_queue.run_repeating(
            self.send_proactivity_message,
            interval=proactivity_interval,
            first=0,
            name="proactivity_message"
        )

