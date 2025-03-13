import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
                          ConversationHandler, filters, CallbackContext)
import os
import api_handler
from dotenv import load_dotenv

# Umgebungsvariablen laden
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

# Logging einrichten
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Definiere Zustände für den Konversationsablauf
(KURS, MENSA, WOHNORT, TRANSPORT, AKTIEN, NEWS) = range(6)

# Definiere Zustände für das Aktualisieren von Präferenzen
(BUTTON, KURS_UPDATE, MENSA_UPDATE, WOHNORT_UPDATE, TRANSPORT_UPDATE, AKTIEN_DELETE, AKTIEN_ADD, NEWS_DELETE, NEWS_ADD) = range(6, 15)

# Nutzer-Daten speichern
user_data_store = {}

async def save_and_ask_next(update: Update, context: CallbackContext, key: str, next_question: str, next_state: int):
    """Speichert die Benutzereingabe und stellt die nächste Frage."""
    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})[key] = update.message.text.strip()  # Antwort speichern
    await update.message.reply_text(next_question)  # Nächste Frage senden
    return next_state  # Zustand zurückgeben

async def start(update: Update, context: CallbackContext):
    """Startet die Unterhaltung."""
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Hallo {user_name}! Ich bin EverydayPDA, dein persönlicher Assistent! 🤖\n"
                                    "Ich werde ein paar Fragen stellen, um dich besser kennenzulernen. 😊")
    await update.message.reply_text("In welchem KURS studierst du? (z. B. IN22)")
    return KURS

async def kurs(update: Update, context: CallbackContext):
    return await save_and_ask_next(update, context, "kurs", "Wo ist deine Mensa (z. B. Mensa Zentral)?", MENSA)

async def mensa(update: Update, context: CallbackContext):
    return await save_and_ask_next(update, context, "mensa", "Wo lebst du?", WOHNORT)

async def wohnort(update: Update, context: CallbackContext):
    return await save_and_ask_next(update, context, "wohnort", "Was ist dein bevorzugtes Transportmittel?", TRANSPORT)

async def transport(update: Update, context: CallbackContext):
    return await save_and_ask_next(update, context, "transport", "Welche Lieblingsaktien hast du? (Mehrere mit Komma trennen)", AKTIEN)

async def aktien(update: Update, context: CallbackContext):
    """Speichert Aktien als Liste und stellt die nächste Frage."""
    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})["aktien"] = [aktie.strip() for aktie in update.message.text.split(",")]
    await update.message.reply_text("Welche bevorzugten Nachrichtenquellen hast du? (Mehrere mit Komma trennen)")
    return NEWS

async def news(update: Update, context: CallbackContext):
    """Speichert Nachrichtenquellen als Liste und zeigt die Zusammenfassung an."""
    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})["news"] = [news.strip() for news in update.message.text.split(",")]
    return await init_end(update, context)

async def init_end(update: Update, context: CallbackContext):
    """Zeigt die Übersicht der Nutzereingaben und speichert die Präferenzen."""
    user_id = update.effective_user.id
    user_info = user_data_store.get(user_id, {})

    summary = (f"Danke für deine Antworten! Hier ist deine Übersicht:\n\n"
               f"📚 Kurs: {user_info.get('kurs', 'Nicht angegeben')}\n"
               f"🍽️ Mensa: {user_info.get('mensa', 'Nicht angegeben')}\n"
               f"🏠 Wohnort: {user_info.get('wohnort', 'Nicht angegeben')}\n"
               f"🚆 Transport: {user_info.get('transport', 'Nicht angegeben')}\n"
               f"📈 Lieblingsaktien: {', '.join(user_info.get('aktien', []))}\n"
               f"📰 Nachrichtenquellen: {', '.join(user_info.get('news', []))}")

    await update.message.reply_text(summary)

    # Speichere die Präferenzen in der Datenbank (falls API vorhanden)
    await update.message.reply_text(api_handler.post_preferences(user_id, user_info))
    await update.message.reply_text("Klicke jederzeit auf das Menü, um die Präferenzen zu ändern.")

    return ConversationHandler.END

async def show_preferences(update: Update, context: CallbackContext):
    await update.message.reply_text(api_handler.get_preferences(update.effective_user.id)[0])

async def preferences(update: Update, context: CallbackContext):
    #if api_handler.get_preferences(update.effective_user.id)[1] == "success":
        await update.message.reply_text(api_handler.get_preferences(update.effective_user.id)[0])
        keyboard = [
            [InlineKeyboardButton("📚 Kurs", callback_data="kurs"), InlineKeyboardButton("🍽️ Mensa", callback_data="mensa")],
            [InlineKeyboardButton("🏠 Wohnort", callback_data="wohnort"), InlineKeyboardButton("🚆 Transport", callback_data="transport")],
            [InlineKeyboardButton("📈 Aktien", callback_data="aktien"), InlineKeyboardButton("📰 Nachrichten", callback_data="news")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Welche Präferenz möchtest du ändern?:", reply_markup=reply_markup)
        return BUTTON
    #else:
        #await update.message.reply_text(api_handler.get_preferences(update.effective_user.id)[0])

async def update_preference(update: Update, context: CallbackContext, state: int, message: str):
    """Echot die Nutzereingabe erstmal zurück."""
    query = update.callback_query

    await query.message.reply_text(message, parse_mode="Markdown")
    return state

# Hier kannst du die Funktionen für die anderen Präferenzen ergänzen
async def kurs_update(update: Update, context: CallbackContext):
    kurs = update.message.text.strip()
    await update.message.reply_text(f"Das ist dein neuer Kurs: {kurs}")
    return ConversationHandler.END

async def mensa_update(update: Update, context: CallbackContext):
    mensa = update.message.text.strip()
    await update.message.reply_text(f"Das ist deine neue Mensa: {mensa}")
    return ConversationHandler.END

async def wohnort_update(update: Update, context: CallbackContext):
    wohnort = update.message.text.strip()
    await update.message.reply_text(f"Das ist dein neuer Wohnort: {wohnort}")
    return ConversationHandler.END 

async def transport_update(update: Update, context: CallbackContext):
    transport = update.message.text.strip()
    await update.message.reply_text(f"Das ist dein neues Transportmittel: {transport}")
    return ConversationHandler.END 

async def aktien_delete(update: Update, context: CallbackContext):
    aktien = update.message.text.strip()
    await update.message.reply_text(f"Das sind deine gelöschten Aktien: {aktien}")
    return ConversationHandler.END

async def aktien_add(update: Update, context: CallbackContext):
    aktien = update.message.text.strip()
    await update.message.reply_text(f"Das sind deine hinzugefügten Aktien: {aktien}")
    return ConversationHandler.END

async def news_delete(update: Update, context: CallbackContext):
    news = update.message.text.strip()
    await update.message.reply_text(f"Das sind deine gelöschten Nachrichtenquellen: {news}")
    return ConversationHandler.END

async def news_add(update: Update, context: CallbackContext): 
    news = update.message.text.strip()
    await update.message.reply_text(f"Das sind deine hinzugefügten Nachrichtenquellen: {news}")
    return ConversationHandler.END

async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "kurs":
        return await update_preference(update, context, KURS_UPDATE, "Was ist dein neuer Kurs?")
    elif query.data == "mensa":
        return await update_preference(update, context, MENSA_UPDATE, "Was ist deine neue Mensa?")
    elif query.data == "wohnort":
        return await update_preference(update, context, WOHNORT_UPDATE, "Was ist dein neuer Wohnort?")
    elif query.data == "transport":
        return await update_preference(update, context, TRANSPORT_UPDATE, "Was ist dein neuer Transport?")
    elif query.data == "aktien":
        keyboard = [
            [InlineKeyboardButton("Aktien löschen", callback_data="aktien_delete")],
            [InlineKeyboardButton("Aktien hinzufügen", callback_data="aktien_add")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Wähle eine Option aus:", reply_markup=reply_markup)
    elif query.data == "news":
        keyboard = [
            [InlineKeyboardButton("Nachrichtenquellen löschen", callback_data="news_delete")],
            [InlineKeyboardButton("Nachrichtenquellen hinzufügen", callback_data="news_add")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Wähle eine Option aus:", reply_markup=reply_markup)
    elif query.data == "aktien_delete":
        return await update_preference(update, context, AKTIEN_DELETE, "Welche Aktien möchtest du entfernen?")
    elif query.data == "aktien_add":
        return await update_preference(update, context, AKTIEN_ADD, "Welche Aktien möchtest du hinzufügen?")
    elif query.data == "news_delete":
        return await update_preference(update, context, NEWS_DELETE, "Welche Nachrichtenquellen möchtest du entfernen?")
    elif query.data == "news_add":
        return await update_preference(update, context, NEWS_ADD, "Welche Nachrichtenquellen möchtest du hinzufügen?")

async def answer(update: Update, context: CallbackContext):
    await update.message.reply_text(api_handler.get_answer(update.message.text))

def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            KURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, kurs)],
            MENSA: [MessageHandler(filters.TEXT & ~filters.COMMAND, mensa)],
            WOHNORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, wohnort)],
            TRANSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, transport)],
            AKTIEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, aktien)],
            NEWS: [MessageHandler(filters.TEXT & ~filters.COMMAND, news)],
        },
        fallbacks=[],
    )

    update_handler = ConversationHandler(
        entry_points=[CommandHandler("changepref", preferences)],
        states={
            BUTTON: [CallbackQueryHandler(button_click)],
            KURS_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kurs_update)],
            MENSA_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, mensa_update)],
            WOHNORT_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, wohnort_update)],
            TRANSPORT_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, transport_update)],
            AKTIEN_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, aktien_delete)],
            AKTIEN_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, aktien_add)],
            NEWS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, news_delete)],
            NEWS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, news_add)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(update_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    application.add_handler(CommandHandler("showpref", show_preferences))


    application.run_polling()

if __name__ == "__main__":
    main()
