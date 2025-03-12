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

# Nutzer-Daten speichern
user_data_store = {}

# Start-Befehl mit Fragenabfolge
async def start(update: Update, context: CallbackContext):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    logger.info(f"User {user_name} mit ID {user_id} hat den Bot gestartet.")

    await update.message.reply_text(f"Hallo {user_name}! Ich bin EverydayPDA, dein persönlicher Assistent! 🤖\nIch werde ein paar Fragen stellen, um dich besser kennen zu lernen. 😊")
    await update.message.reply_text("Was studierst du?  (z. B. Informatik)")
    
    return KURS

async def kurs(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id] = {"kurs": update.message.text}
    await update.message.reply_text("Wo ist deine Mensa (z. B. Mensa Zentral)?")
    return MENSA

async def mensa(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id]["mensa"] = update.message.text
    await update.message.reply_text("Wo lebst du?")
    return WOHNORT

async def wohnort(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id]["wohnort"] = update.message.text
    await update.message.reply_text("Was ist dein bevorzugtes Transportmittel?")
    return TRANSPORT

async def transport(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id]["transport"] = update.message.text
    await update.message.reply_text("Welche Lieblingsaktien hast du? (Mehrere mit Komma trennen)")
    return AKTIEN

async def aktien(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id]["aktien"] = [aktie.strip() for aktie in update.message.text.split(",")]
    await update.message.reply_text("Welche bevorzugten Nachrichtenquellen hast du? (Mehrere mit Komma trennen)")
    return NEWS

async def news(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id]["news"] = [news.strip() for news in update.message.text.split(",")]

    user_info = user_data_store[update.effective_user.id]
    summary = (f"Danke für deine Antworten! Hier ist deine Übersicht:\n\n"
               f"📚 Kurs: {user_info['kurs']}\n"
               f"🍽️ Mensa: {user_info['mensa']}\n"
               f"🏠 Wohnort: {user_info['wohnort']}\n"
               f"🚆 Transport: {user_info['transport']}\n"
               f"📈 Lieblingsaktien: {', '.join(user_info['aktien'])}\n"
               f"📰 Nachrichtenquellen: {', '.join(user_info['news'])}")

    await update.message.reply_text(summary)
    
    # Speichere die Präferenzen in der Datenbank
    print(user_info["aktien"])
    print(user_info["news"])
    await update.message.reply_text(api_handler.post_preferences(update.effective_user.id, user_info))


    await update.message.reply_text("Klicke jederzeit auf das Menü, um die Präferenzen zu ändern.")



    return ConversationHandler.END

async def preferences(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Kurs", callback_data="kurs"), InlineKeyboardButton("Mensa", callback_data="mensa")],
        [InlineKeyboardButton("Wohnort", callback_data="wohnort"), InlineKeyboardButton("Transport", callback_data="transport")],
        [InlineKeyboardButton("Aktien", callback_data="aktien"), InlineKeyboardButton("Nachrichten", callback_data="news")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welche Präferenz möchtest du ändern?:", reply_markup=reply_markup)

async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "kurs":
        await query.message.reply_text("Was ist dein neuer Kurs?", parse_mode="Markdown")
    elif query.data == "mensa":
        await query.message.reply_text("Was ist deine neue Mensa?", parse_mode="Markdown")
    elif query.data == "wohnort":
        await query.message.reply_text("Was ist dein neuer Wohnort?", parse_mode="Markdown")
    elif query.data == "transport":
        await query.message.reply_text("Was ist dein neues Transportmittel?", parse_mode="Markdown")
    elif query.data == "aktien":
        keyboard = [
            [InlineKeyboardButton("Aktien löschen", callback_data="aktien_delete")],
            [InlineKeyboardButton("Aktien hinzufügen", callback_data="aktien_add")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Wähle eine Option aus:", reply_markup=reply_markup)
    elif query.data == "news":
        keyboard = [
            [InlineKeyboardButton("Kurs", callback_data="news_delete")],
            [InlineKeyboardButton("Mensa", callback_data="news_add")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Wähle eine Option aus:", reply_markup=reply_markup)
    elif query.data == "aktien_delete":
        await query.message.reply_text("Welche Aktien möchtest du löschen?", parse_mode="Markdown")
    elif query.data == "aktien_add":
        await query.message.reply_text("Welche Aktien möchtest du hinzufügen?", parse_mode="Markdown")
    elif query.data == "news_delete":
        await query.message.reply_text("Welche Nachrichtenquellen möchtest du löschen?", parse_mode="Markdown")
    elif query.data == "news_add":
        await query.message.reply_text("Welche Nachrichtenquellen möchtest du hinzufügen?", parse_mode="Markdown")

async def echo(update: Update, context: CallbackContext):
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

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("preferences", preferences))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()

if __name__ == "__main__":
    main()
