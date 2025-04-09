import unittest
from unittest.mock import AsyncMock, patch
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging

# Angenommene Funktion, die wir testen möchten:
from bot import start, course, cafeteria, user_data_store, api_client, answer, button_click, course_update, show_preferences  # Beispiel-Import

class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        """Einrichtung der Tests"""
        self.mock_update = AsyncMock(spec=Update)  # Mock für Update-Objekt
        self.mock_context = AsyncMock(spec=CallbackContext)  # Mock für CallbackContext
        self.mock_user_id = 1234
        self.mock_update.effective_user.id = self.mock_user_id
        self.mock_update.message.text = "IN22"  # Beispieltext

    @patch("my_module.api_handler.post_preferences")
    @patch("telegram.Update.message.reply_text")
    async def test_start(self, mock_reply_text, mock_post_preferences):
        """Test für den Start-Handler"""
        # Mock das Reply
        mock_reply_text.return_value = None

        # Führe den Handler aus
        await start(self.mock_update, self.mock_context)

        # Überprüfen, ob der Text richtig zurückgesendet wurde
        mock_reply_text.assert_any_call("Hallo None mit der User-ID: 1234! Ich bin EverydayPDA, dein persönlicher Assistent! 🤖\nIch werde ein paar Fragen stellen, um dich besser kennenzulernen. 😊")
        mock_reply_text.assert_any_call("In welchem KURS studierst du? (z. B. IN22)")

    @patch("my_module.api_handler.put_preference")
    @patch("telegram.Update.message.reply_text")
    async def test_kurs(self, mock_reply_text, mock_put_preference):
        """Test für den Kurs-Handler"""
        user_data_store[self.mock_user_id] = {}  # Leeren Speicher simulieren

        # Mock das Reply
        mock_reply_text.return_value = None

        # Führe den Handler aus
        await course(self.mock_update, self.mock_context)

        # Überprüfen, ob die Antwort richtig gesendet wurde
        mock_reply_text.assert_any_call("Wo ist deine Mensa (z. B. Mensa Central)?")
        # Überprüfen, ob die Benutzereingabe gespeichert wurde
        self.assertEqual(user_data_store[self.mock_user_id]["kurs"], "IN22")

    @patch("my_module.api_handler.get_preferences")
    @patch("telegram.Update.message.reply_text")
    async def test_show_preferences(self, mock_reply_text, mock_get_preferences):
        """Test für den Show Preferences-Handler"""
        # Simuliere eine API-Antwort
        mock_get_preferences.return_value = ["Test Preferences", "success"]

        # Führe den Handler aus
        await show_preferences(self.mock_update, self.mock_context)

        # Überprüfen, ob die Antwort korrekt war
        mock_reply_text.assert_any_call("Test Preferences")

    @patch("my_module.api_handler.put_preference")
    @patch("telegram.Update.message.reply_text")
    async def test_update_preference(self, mock_reply_text, mock_put_preference):
        """Test für das Update von Präferenzen"""
        mock_put_preference.return_value = "success"

        # Simuliere, dass der Benutzer 'IN23' als neuen Kurs eingibt
        self.mock_update.message.text = "IN23"

        # Führe den Handler aus (Kurs-Update Beispiel)
        await course_update(self.mock_update, self.mock_context)

        # Überprüfen, ob der API-Aufruf gemacht wurde
        mock_put_preference.assert_called_once_with(self.mock_user_id, "course", "IN23")
        mock_reply_text.assert_any_call("success")

    @patch("telegram.Update.message.reply_text")
    async def test_button_click(self, mock_reply_text):
        """Test für den Button Click-Handler"""
        query = AsyncMock()  # Simuliere CallbackQuery
        query.data = "kurs"
        query.message.reply_text = mock_reply_text

        # Führe den Handler aus
        await button_click(self.mock_update, self.mock_context)

        # Überprüfen, ob die Nachricht korrekt gesendet wurde
        mock_reply_text.assert_any_call("Was ist dein neuer Kurs?")

    @patch("telegram.Update.message.reply_text")
    async def test_answer(self, mock_reply_text):
        """Test für die Antwort-Funktion"""
        self.mock_update.message.text = "Testfrage"
        
        # Mock die API-Antwort
        with patch("my_module.api_handler.get_answer", return_value="Antwort von der API"):
            await answer(self.mock_update, self.mock_context)

        # Überprüfen, ob die API-Antwort korrekt gesendet wurde
        mock_reply_text.assert_any_call("Antwort von der API")

if __name__ == "__main__":
    unittest.main()
