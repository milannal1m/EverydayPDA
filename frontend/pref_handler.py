from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext

from pref_config import (
    BUTTON, CAFETERIA_UPDATE, CITY_UPDATE, TRANSPORT_UPDATE, 
    STOCKS_DELETE, STOCKS_ADD, NEWS_DELETE, NEWS_ADD
)
import api_client

class PreferenceHandler:
    def __init__(self):
        pass

    async def ask_user_for_preference_change(self, update: Update, context: CallbackContext, state: int, message: str):
        """Fragt den Benutzer nach einem neuen Eintrag für die Präferenz."""
        query = update.callback_query
        await query.message.reply_text(message, parse_mode="Markdown")
        return state


    async def get_summary(self, update: Update, context: CallbackContext):
        prefs, status = api_client.get_preferences(update.effective_user.id)
        if status == "success":
            summary = (f"Hier ist deine Übersicht:\n\n"
            f"📚 Kurs: {prefs['course']}\n"
            f"🍽️ Mensa: {prefs['cafeteria']}\n"
            f"🏠 Wohnort: {prefs['city']}\n"
            f"🚆 Transport: {prefs['preferred_transport_medium']}\n"
            f"📈 Lieblingsaktien: {', '.join(prefs['stocks'])}\n"
            f"📰 Nachrichtenquellen: {', '.join(prefs['news'])}")
            return summary
        else:
            return "Du hast noch keine Präferenzen festgelegt. Starte den Einrichtungsprozess mit /start."


    async def show_preferences(self, update: Update, context: CallbackContext):
        """Zeigt die bestehenden Präferenzen oder startet den Einrichtungsprozess, falls keine vorhanden sind."""
        text = await self.get_summary(update, context)
        await update.message.reply_text(text)


    async def start_change_preferences(self, update: Update, context: CallbackContext):
        """Ermöglicht das Anschauen und Ändern von Präferenzen."""
        text = await self.get_summary(update, context)
        await update.message.reply_text(text)
        keyboard = [
            [
                InlineKeyboardButton("🍽️ Mensa", callback_data="cafeteria")
            ],
            [
                InlineKeyboardButton("🏠 Wohnort", callback_data="city")
            ],
            [
                InlineKeyboardButton("🚆 Transport", callback_data="transport")
            ],
            [
                InlineKeyboardButton("📈 Aktien", callback_data="stocks")
            ],
            [
                InlineKeyboardButton("📰 Nachrichten", callback_data="news")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welche Präferenz möchtest du ändern?:",
            reply_markup=reply_markup
        )
        return BUTTON


    async def change_cafeteria(self, update: Update, context: CallbackContext):
        new_cafeteria = update.message.text.strip()
        response = api_client.put_preference(update.effective_user.id, "cafeteria", new_cafeteria)
        await update.message.reply_text(response)
        return ConversationHandler.END


    async def change_city(self, update: Update, context: CallbackContext):
        new_residence = update.message.text.strip()
        response = api_client.put_preference(update.effective_user.id, "city", new_residence)
        await update.message.reply_text(response)
        return ConversationHandler.END


    async def change_transport(self, update: Update, context: CallbackContext):
        new_transport = update.message.text.strip()
        response = api_client.put_preference(
            update.effective_user.id, "preferred_transport_medium", new_transport
        )
        await update.message.reply_text(response)
        return ConversationHandler.END


    async def remove_stocks(self, update: Update, context: CallbackContext):
        stocks = [s.strip() for s in update.message.text.split(",")]
        response = api_client.put_preference(update.effective_user.id, "delete_stocks", stocks)
        await update.message.reply_text(response)
        return ConversationHandler.END


    async def add_stocks(self, update: Update, context: CallbackContext):
        stocks = [s.strip() for s in update.message.text.split(",")]
        response = api_client.put_preference(update.effective_user.id, "add_stocks", stocks)
        await update.message.reply_text(response)
        return ConversationHandler.END


    async def remove_news(self, update: Update, context: CallbackContext):
        chosen_news = [n.strip() for n in update.message.text.split(",")]
        response = api_client.put_preference(update.effective_user.id, "delete_news", chosen_news)
        await update.message.reply_text(response)
        return ConversationHandler.END


    async def add_news(self, update: Update, context: CallbackContext):
        chosen_news = [n.strip() for n in update.message.text.split(",")]
        response = api_client.put_preference(update.effective_user.id, "add_news", chosen_news)
        await update.message.reply_text(response)
        return ConversationHandler.END


    async def process_preference_button_click(self, update: Update, context: CallbackContext):
        """Bearbeitet die Button-Klicks für das Ändern der Präferenzen."""
        query = update.callback_query
        await query.answer()

        if query.data == "cafeteria":
            return await self.ask_user_for_preference_change(update, context, CAFETERIA_UPDATE, "Was ist deine neue Mensa?")
        elif query.data == "city":
            return await self.ask_user_for_preference_change(update, context, CITY_UPDATE, "Was ist dein neuer Wohnort?")
        elif query.data == "transport":
            return await self.ask_user_for_preference_change(update, context, TRANSPORT_UPDATE, "Was ist dein neuer Transport?")
        elif query.data == "stocks":
            keyboard = [
                [InlineKeyboardButton("Aktien löschen", callback_data="stocks_delete")],
                [InlineKeyboardButton("Aktien hinzufügen", callback_data="stocks_add")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Wähle eine Option aus:", reply_markup=reply_markup)
        elif query.data == "news":
            keyboard = [
                [InlineKeyboardButton("Nachrichtenthemen löschen", callback_data="news_delete")],
                [InlineKeyboardButton("Nachrichtenthemen hinzufügen", callback_data="news_add")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Wähle eine Option aus:", reply_markup=reply_markup)
        elif query.data == "stocks_delete":
            return await self.ask_user_for_preference_change(
                update, context, STOCKS_DELETE, "Welche Aktien möchtest du entfernen?"
            )
        elif query.data == "stocks_add":
            return await self.ask_user_for_preference_change(
                update, context, STOCKS_ADD, "Welche Aktien möchtest du hinzufügen?"
            )
        elif query.data == "news_delete":
            return await self.ask_user_for_preference_change(
                update, context, NEWS_DELETE, "Welche Nachrichtenthemen möchtest du entfernen?"
            )
        elif query.data == "news_add":
            return await self.ask_user_for_preference_change(
                update, context, NEWS_ADD, "Welche Nachrichtenthemen möchtest du hinzufügen?"
            )