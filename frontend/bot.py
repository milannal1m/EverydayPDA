import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    CallbackContext
)
from dotenv import load_dotenv
import api_client
import speech_utils

# Load environment variables
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation flow states (German text remains in user replies)
(COURSE, CAFETERIA, CITY, TRANSPORT, STOCKS, NEWS) = range(6)

# Define states for updating preferences
(
    BUTTON,
    COURSE_UPDATE,
    CAFETERIA_UPDATE,
    CITY_UPDATE,
    TRANSPORT_UPDATE,
    STOCKS_DELETE,
    STOCKS_ADD,
    NEWS_DELETE,
    NEWS_ADD
) = range(6, 15)

# Store user data
user_data_store = {}

NEWS_CATEGORIES = [
    "business", 
    "entertainment", 
    "general", 
    "health", 
    "science", 
    "sports", 
    "technology"
]

async def save_and_ask_next(update: Update, 
                            context: CallbackContext,                         
                            key: str,                             
                            next_question: str,                             
                            next_state: int):
    """Speichert die Benutzereingabe und stellt die nächste Frage."""
    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})[key] = update.message.text.strip()
    await update.message.reply_text(next_question)
    return next_state


async def start(update: Update, context: CallbackContext):
    """
    Starts the conversation (German text output).
    """
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"Hallo {user_name} mit der User-ID: {user_id}! Ich bin EverydayPDA, "
        "dein persönlicher Assistent! 🤖\n"
        "Ich werde ein paar Fragen stellen, um dich besser kennenzulernen. 😊"
    )
    await update.message.reply_text("In welchem KURS studierst du? (z. B. IN22)")
    return COURSE


async def course(update: Update, context: CallbackContext):
    """
    Handles the user's input for 'course'.
    """
    return await save_and_ask_next(
        update,
        context,
        "course",
        "Wo ist deine Mensa (z. B. Mensa Central)?",
        CAFETERIA
    )


async def cafeteria(update: Update, context: CallbackContext):
    """
    Handles the user's input for 'cafeteria'.
    """
    return await save_and_ask_next(
        update,
        context,
        "cafeteria",
        "Wo lebst du?",
        CITY
    )


async def city(update: Update, context: CallbackContext):
    """
    Handles the user's input for 'city'.
    """
    return await save_and_ask_next(
        update,
        context,
        "city",
        "Was ist dein bevorzugtes Transportmittel?",
        TRANSPORT
    )


async def transport(update: Update, context: CallbackContext):
    """
    Handles the user's input for 'transport'.
    """
    return await save_and_ask_next(
        update,
        context,
        "transport",
        "Welche Lieblingsaktien hast du? (Bitte als Tickersymbole mit Komma getrennt angeben)",
        STOCKS
    )


async def stocks(update: Update, context: CallbackContext):
    """
    Stores stocks as a list, then leads to the next question.
    """
    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})["stocks"] = [
        stock.strip() for stock in update.message.text.split(",")
    ]
    await update.message.reply_text("Was sind deine bevorzugten Nachrichtenthemen?")
    return await news(update, context)


async def news(update: Update, context: CallbackContext):
    """
    Initializes 'selected_news' and displays an inline keyboard with news categories.
    """
    context.user_data["selected_news"] = []
    keyboard = build_news_keyboard(context.user_data["selected_news"])
    await update.message.reply_text(
        "Wähle deine bevorzugten Nachrichtenthemen:",
        reply_markup=keyboard
    )
    return NEWS


def build_news_keyboard(selected):
    """
    Dynamically builds an inline keyboard for choosing news categories.
    """
    inline_buttons = []
    for cat in NEWS_CATEGORIES:
        label = cat + (" ✔" if cat in selected else "")
        inline_buttons.append([
            InlineKeyboardButton(label, callback_data=f"news:{cat}")
        ])
    inline_buttons.append([
        InlineKeyboardButton("Fertig", callback_data="news:submit")
    ])
    return InlineKeyboardMarkup(inline_buttons)


async def news_callback(update: Update, context: CallbackContext):
    """
    Handles user interactions with the news categories inline keyboard.
    """
    query = update.callback_query
    await query.answer()

    if "selected_news" not in context.user_data:
        context.user_data["selected_news"] = []

    data = query.data.split(":", 1)
    if len(data) == 2 and data[0] == "news":
        if data[1] == "submit":
            print("hat geklappt")
            # Save selection and show final summary
            user_id = query.from_user.id
            user_data_store.setdefault(user_id, {})["news"] = context.user_data["selected_news"]
            joined_news = ", ".join(context.user_data["selected_news"])
            await query.edit_message_text(f"Deine Nachrichtenthemen: {joined_news}")
            return await init_end(update, context)

        # Select or deselect a category
        category = data[1]
        if category in context.user_data["selected_news"]:
            context.user_data["selected_news"].remove(category)
        else:
            context.user_data["selected_news"].append(category)

        # Update keyboard with checks
        new_keyboard = build_news_keyboard(context.user_data["selected_news"])
        await query.edit_message_reply_markup(reply_markup=new_keyboard)

    return NEWS


async def init_end(update: Update, context: CallbackContext):
    """
    Shows an overview of the user's inputs (German) and saves preferences.
    """
    user_id = update.effective_user.id
    user_info = user_data_store.get(user_id, {})

    summary = (
        "Danke für deine Antworten! Hier ist deine Übersicht:\n\n"
        f"📚 Kurs: {user_info.get('course', 'Nicht angegeben')}\n"
        f"🍽️ Mensa: {user_info.get('cafeteria', 'Nicht angegeben')}\n"
        f"🏠 Wohnort: {user_info.get('city', 'Nicht angegeben')}\n"
        f"🚆 Transport: {user_info.get('transport', 'Nicht angegeben')}\n"
        f"📈 Lieblingsaktien: {', '.join(user_info.get('stocks', []))}\n"
        f"📰 Nachrichtenthemen: {', '.join(user_info.get('news', []))}"
    )

    # Check if the message comes from a CallbackQuery
    if update.message:
        await update.message.reply_text(summary)
        # Save preferences in the database (if available)
        await update.message.reply_text(api_client.post_preferences(user_id, user_info))
        await update.message.reply_text(
            "Klicke jederzeit auf das Menü, um die Präferenzen zu ändern."
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(summary)
        # Save preferences in the database (if available)
        await update.callback_query.message.reply_text(api_client.post_preferences(user_id, user_info))
        await update.callback_query.message.reply_text(
            "Klicke jederzeit auf das Menü, um die Präferenzen zu ändern."
        )

    return ConversationHandler.END


async def show_preferences(update: Update, context: CallbackContext):
    """
    Displays existing preferences or starts the setup if none are found.
    """
    prefs, status = api_client.get_preferences(update.effective_user.id)
    if status == "success":
        await update.message.reply_text(prefs)
    else:
        await update.message.reply_text(
            "Du hast noch keine Präferenzen festgelegt. Starte jetzt den Einrichtungsprozess:"
        )
        return await start(update, context)


async def preferences(update: Update, context: CallbackContext):
    """
    Allows the user to view and change existing preferences.
    """
    print("Preferences wurde aufgerufen!")
    prefs, status = api_client.get_preferences(update.effective_user.id)
    if status == "success":
        await update.message.reply_text(prefs)
        keyboard = [
            [
                InlineKeyboardButton("📚 Kurs", callback_data="course"),
                InlineKeyboardButton("🍽️ Mensa", callback_data="cafeteria")
            ],
            [
                InlineKeyboardButton("🏠 Wohnort", callback_data="city"),
                InlineKeyboardButton("🚆 Transport", callback_data="transport")
            ],
            [
                InlineKeyboardButton("📈 Aktien", callback_data="stocks"),
                InlineKeyboardButton("📰 Nachrichten", callback_data="news")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Welche Präferenz möchtest du ändern?:",
            reply_markup=reply_markup
        )
        return BUTTON
    else:
        await update.message.reply_text(
            "Du hast noch keine Präferenzen festgelegt. Starte jetzt den Einrichtungsprozess:"
        )
        return await start(update, context)


async def update_preference(update: Update,
                            context: CallbackContext,
                            state: int,
                            message: str):
    """
    Prompts the user for a new preference entry (German text).
    """
    query = update.callback_query
    await query.message.reply_text(message, parse_mode="Markdown")
    return state


# UPDATE PREFERENCES
async def course_update(update: Update, context: CallbackContext):
    new_course = update.message.text.strip()
    response = api_client.put_preference(update.effective_user.id, "course", new_course)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def cafeteria_update(update: Update, context: CallbackContext):
    new_cafeteria = update.message.text.strip()
    response = api_client.put_preference(update.effective_user.id, "cafeteria", new_cafeteria)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def city_update(update: Update, context: CallbackContext):
    new_residence = update.message.text.strip()
    response = api_client.put_preference(update.effective_user.id, "city", new_residence)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def transport_update(update: Update, context: CallbackContext):
    new_transport = update.message.text.strip()
    response = api_client.put_preference(
        update.effective_user.id, "preferred_transport_medium", new_transport
    )
    await update.message.reply_text(response)
    return ConversationHandler.END


async def stocks_delete(update: Update, context: CallbackContext):
    stocks = [s.strip() for s in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "delete_stocks", stocks)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def stocks_add(update: Update, context: CallbackContext):
    stocks = [s.strip() for s in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "add_stocks", stocks)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def news_delete(update: Update, context: CallbackContext):
    chosen_news = [n.strip() for n in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "delete_news", chosen_news)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def news_add(update: Update, context: CallbackContext):
    chosen_news = [n.strip() for n in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "add_news", chosen_news)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def button_click(update: Update, context: CallbackContext):
    """
    Handles button clicks for updating various preferences.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "course":
        return await update_preference(update, context, COURSE_UPDATE, "Was ist dein neuer Kurs?")
    elif query.data == "cafeteria":
        return await update_preference(update, context, CAFETERIA_UPDATE, "Was ist deine neue Mensa?")
    elif query.data == "city":
        return await update_preference(update, context, CITY_UPDATE, "Was ist dein neuer Wohnort?")
    elif query.data == "transport":
        return await update_preference(update, context, TRANSPORT_UPDATE, "Was ist dein neuer Transport?")
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
        return await update_preference(
            update, context, STOCKS_DELETE, "Welche Aktien möchtest du entfernen?"
        )
    elif query.data == "stocks_add":
        return await update_preference(
            update, context, STOCKS_ADD, "Welche Aktien möchtest du hinzufügen?"
        )
    elif query.data == "news_delete":
        return await update_preference(
            update, context, NEWS_DELETE, "Welche Nachrichtenthemen möchtest du entfernen?"
        )
    elif query.data == "news_add":
        return await update_preference(
            update, context, NEWS_ADD, "Welche Nachrichtenthemen möchtest du hinzufügen?"
        )


async def answer(update: Update, context: CallbackContext):
    """
    Handles both voice and text messages by sending replies in German.
    """
    if update.message.voice:
        voice_path = os.path.join(BASE_DIR, "output.ogg")
        voice_file = await update.message.voice.get_file()
        await voice_file.download_to_drive(voice_path)

        input_text = speech_utils.convert_voice_to_text(voice_path)
        text = api_client.get_answer(input_text, update.effective_user.id)
    else:
        text = api_client.get_answer(update.message.text, update.effective_user.id)

    voice_output_path = speech_utils.generate_voice_message(text)

    # Send both text and voice response
    await update.message.reply_text(text)
    await update.message.reply_voice(voice=open(voice_output_path, "rb"))


async def morning_message(update: Update, context: CallbackContext):
    """
    Sends a morning message (German text) and its voice version.
    """
    text = api_client.get_morning_message(update.effective_user.id)
    voice_output_path = speech_utils.generate_voice_message(text)

    await update.message.reply_text(text)
    await update.message.reply_voice(voice=open(voice_output_path, "rb"))


def main():
    """
    Main entry point for running the bot. 
    """
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    init_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course)],
            CAFETERIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, cafeteria)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            TRANSPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, transport)],
            STOCKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, stocks)],
            NEWS: [CallbackQueryHandler(news_callback, pattern=r"^news:")],
        },
        fallbacks=[]
    )

    update_handler = ConversationHandler(
        entry_points=[CommandHandler("changepref", preferences)],
        states={
            BUTTON: [CallbackQueryHandler(button_click)],
            COURSE_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course_update)],
            CAFETERIA_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cafeteria_update)],
            CITY_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_update)],
            TRANSPORT_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, transport_update)],
            STOCKS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, stocks_delete)],
            STOCKS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, stocks_add)],
            NEWS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, news_delete)],
            NEWS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, news_add)],
        },
        fallbacks=[]
    )

    # Add handlers
    application.add_handler(init_handler)
    application.add_handler(update_handler)
    application.add_handler(
        MessageHandler((filters.TEXT & ~filters.COMMAND) | filters.VOICE, answer)
    )
    application.add_handler(CommandHandler("showpref", show_preferences))
    application.add_handler(CommandHandler("morning", morning_message))

    # Start polling
    application.run_polling()


if __name__ == "__main__":
    main()
