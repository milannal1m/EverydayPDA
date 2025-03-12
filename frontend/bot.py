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
    
    return KURS  # Wechselt in den Zustand "KURS"

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
    await update.message.reply_text("Was sind deine Lieblingsaktien? (z. B. Apple, Tesla)")
    return AKTIEN

async def aktien(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id]["aktien"] = update.message.text
    await update.message.reply_text("Was ist deine bevorzugte Nachrichtenquelle?")
    return NEWS

async def news(update: Update, context: CallbackContext):
    user_data_store[update.effective_user.id]["news"] = update.message.text

    # Zeige die gesammelten Daten an
    user_info = user_data_store[update.effective_user.id]
    summary = (f"Danke für deine Antworten! Hier ist deine Übersicht:\n\n"
               f"📚 Kurs: {user_info['kurs']}\n"
               f"🍽️ Mensa: {user_info['mensa']}\n"
               f"🏠 Wohnort: {user_info['wohnort']}\n"
               f"🚆 Transport: {user_info['transport']}\n"
               f"📈 Lieblingsaktien: {user_info['aktien']}\n"
               f"📰 Nachrichtenquelle: {user_info['news']}")

    await update.message.reply_text(summary)
    await update.message.reply_text("Gib /menu ein, um das Menü zu öffnen.")

    return ConversationHandler.END  # Beendet die Konversation

# Menü anzeigen
async def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Hilfe", callback_data="help")],
        [InlineKeyboardButton("Präferenzen", callback_data="preferences")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bitte wähle eine Option:", reply_markup=reply_markup)

# Antwort auf Menü-Buttons
async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await query.message.reply_text("Hier ist die Github-Seite: [Link zur Hilfe](https://github.com/milannal1m/EverydayPDA)", parse_mode="Markdown")
    elif query.data == "preferences":
        await query.message.reply_text("Hier kannst du in Zukunft deine Präferenzen ändern. Gerade geht es noch nicht. 😅")

# Echo-Handler für normale Nachrichten
async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(api_handler.get_answer(update.message.text))

# Hauptfunktion
def main():
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # ConversationHandler für die Fragen
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

    # Befehle und Handler hinzufügen
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Startet den Bot
    application.run_polling()

if __name__ == "__main__":
    main()
