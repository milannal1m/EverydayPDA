import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    CallbackContext, CallbackQueryHandler, filters
)

import api_client

# Logging
logger = logging.getLogger(__name__)

# Define conversation flow states (für die Einrichtung)
(
    COURSE, 
    CAFETERIA, 
    CITY, 
    TRANSPORT, 
    STOCKS, 
    NEWS
) = range(6)

# Zustände für Updates
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

# Kategorien für Nachrichten und Transport
NEWS_CATEGORIES = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology"
]

TRANSPORT_CATEGORIES = [
    "driving-car",
    "cycling-regular",
    "foot-walking",
]

# Lokale Speicherung der Nutzerdaten
user_data_store = {}

##############################################
# /START HANDLER: Einrichtungsprozess
##############################################

async def start_initialization(update: Update, context: CallbackContext):
    """Startet die Konversation zur Einrichtung."""
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"Hallo {user_name} mit der User-ID: {user_id}! Ich bin EverydayPDA, "
        "dein persönlicher Assistent! 🤖\n"
        "Ich werde ein paar Fragen stellen, um dich besser kennenzulernen. 😊"
    )
    await update.message.reply_text("In welchem KURS studierst du? (z. B. IN22)")
    return COURSE


async def initialize_course(update: Update, context: CallbackContext):
    """Bearbeitet die Eingabe des Kurses."""
    key = "course"
    next_question = "Wo ist deine Mensa (z. B. Mensa Central)?"

    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})[key] = update.message.text.strip()
    await update.message.reply_text(next_question)
    return CAFETERIA


async def initialize_cafeteria(update: Update, context: CallbackContext):
    """Bearbeitet die Eingabe zur Mensa."""
    key = "cafeteria"
    next_question = "Wo lebst du? (z. B. Berlin, München, etc.)"
    
    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})[key] = update.message.text.strip()
    await update.message.reply_text(next_question)
    return CITY


async def initialize_city(update: Update, context: CallbackContext):
    """Bearbeitet die Eingabe des Wohnorts."""
    key = "city"
    next_question = "Was ist dein bevorzugtes Transportmittel?"

    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})[key] = update.message.text.strip()
    await update.message.reply_text(next_question)
    return await initialize_transport(update, context)


async def initialize_transport(update: Update, context: CallbackContext):
    """Zeigt eine Inline-Tastatur zur Auswahl des bevorzugten Transports und verarbeitet die Auswahl."""
    # Interne Hilfsfunktion zum Erstellen der Inline-Tastatur
    def build_transport_keyboard():
        buttons = []
        for mode in TRANSPORT_CATEGORIES:
            buttons.append([InlineKeyboardButton(mode, callback_data=f"transport:{mode}")])
        return InlineKeyboardMarkup(buttons)

    if update.message:
        # Bei der ersten Ausführung: Zeige die Auswahl
        keyboard = build_transport_keyboard()
        await update.message.reply_text(
            "Wähle aus diesen Optionen:",
            reply_markup=keyboard
        )
        return TRANSPORT

    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        data = query.data.split(":", 1)
        if len(data) == 2 and data[0] == "transport":
            chosen_transport = data[1]
            user_id = update.effective_user.id
            user_data_store.setdefault(user_id, {})["transport"] = chosen_transport
            await query.edit_message_text(f"Dein bevorzugtes Transportmittel: {chosen_transport}")
            # Frage zum nächsten Schritt: Aktien
            await query.message.reply_text(
                "Welche Lieblingsaktien hast du? (Bitte als Tickersymbole mit Komma getrennt angeben)"
            )
            return STOCKS
        return TRANSPORT


async def initialize_stocks(update: Update, context: CallbackContext):
    """Speichert die Aktien als Liste und leitet zur nächsten Frage über."""
    user_id = update.effective_user.id
    user_data_store.setdefault(user_id, {})["stocks"] = [
        stock.strip() for stock in update.message.text.split(",")
    ]
    await update.message.reply_text("An welchen Nachrichtenthemen bist du interessiert?")
    return await initialize_news(update, context)


async def initialize_news(update: Update, context: CallbackContext):
    """
    Diese Funktion übernimmt sowohl das Initialisieren der Nachrichtenthemen-Auswahl als auch
    die Verarbeitung der Callback-Daten, wenn der Benutzer eine Kategorie auswählt oder bestätigt.
    """
    # Interne Hilfsfunktion zum Erstellen der Inline-Tastatur
    def build_news_keyboard(selected):
        inline_buttons = []
        for cat in NEWS_CATEGORIES:
            label = cat + (" ✔" if cat in selected else "")
            inline_buttons.append([InlineKeyboardButton(label, callback_data=f"news:{cat}")])
        inline_buttons.append([InlineKeyboardButton("Fertig", callback_data="news:submit")])
        return InlineKeyboardMarkup(inline_buttons)

    # Initialisierungsfall (wird beim ersten Aufruf über eine Textnachricht getriggert)
    if update.message:
        context.user_data["selected_news"] = []
        keyboard = build_news_keyboard(context.user_data["selected_news"])
        await update.message.reply_text(
            "Wähle aus diesen Optionen:",
            reply_markup=keyboard
        )
        return NEWS

    # Callback-Fall: Verarbeitung der Auswahl über die Inline-Tastatur
    elif update.callback_query:
        query = update.callback_query
        await query.answer()

        if "selected_news" not in context.user_data:
            context.user_data["selected_news"] = []

        data = query.data.split(":", 1)
        if len(data) == 2 and data[0] == "news":
            if data[1] == "submit":
                user_id = query.from_user.id
                user_data_store.setdefault(user_id, {})["news"] = context.user_data["selected_news"]
                joined_news = ", ".join(context.user_data["selected_news"])
                await query.edit_message_text(f"Deine Nachrichtenthemen: {joined_news}")
                return await end_initialization(update, context)

            category = data[1]
            if category in context.user_data["selected_news"]:
                context.user_data["selected_news"].remove(category)
            else:
                context.user_data["selected_news"].append(category)

            new_keyboard = build_news_keyboard(context.user_data["selected_news"])
            await query.edit_message_reply_markup(reply_markup=new_keyboard)

        return NEWS


async def end_initialization(update: Update, context: CallbackContext):
    """Zeigt eine Zusammenfassung der Benutzereingaben und speichert die Präferenzen."""
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

    if update.message:
        await update.message.reply_text(summary)
        await update.message.reply_text(api_client.post_preferences(user_id, user_info))
        await update.message.reply_text(
            "Klicke jederzeit auf das Menü, um die Präferenzen zu ändern."
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(summary)
        await update.callback_query.message.reply_text(api_client.post_preferences(user_id, user_info))
        await update.callback_query.message.reply_text(
            "Klicke jederzeit auf das Menü, um die Präferenzen zu ändern."
        )

    return ConversationHandler.END


##############################################
# /SHOWPREF & /CHANGEPREF HANDLERS
##############################################

async def ask_user_for_preference_change(update: Update, context: CallbackContext, state: int, message: str):
    """Fragt den Benutzer nach einem neuen Eintrag für die Präferenz."""
    query = update.callback_query
    await query.message.reply_text(message, parse_mode="Markdown")
    return state


async def get_summary(update: Update, context: CallbackContext):
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


async def show_preferences(update: Update, context: CallbackContext):
    """Zeigt die bestehenden Präferenzen oder startet den Einrichtungsprozess, falls keine vorhanden sind."""
    text = await get_summary(update, context)
    await update.message.reply_text(text)


async def start_change_preferences(update: Update, context: CallbackContext):
    """Ermöglicht das Anschauen und Ändern von Präferenzen."""
    text = await get_summary(update, context)
    await update.message.reply_text(text)
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


async def change_course(update: Update, context: CallbackContext):
    new_course = update.message.text.strip()
    response = api_client.put_preference(update.effective_user.id, "course", new_course)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def change_cafeteria(update: Update, context: CallbackContext):
    new_cafeteria = update.message.text.strip()
    response = api_client.put_preference(update.effective_user.id, "cafeteria", new_cafeteria)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def change_city(update: Update, context: CallbackContext):
    new_residence = update.message.text.strip()
    response = api_client.put_preference(update.effective_user.id, "city", new_residence)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def change_transport(update: Update, context: CallbackContext):
    new_transport = update.message.text.strip()
    response = api_client.put_preference(
        update.effective_user.id, "preferred_transport_medium", new_transport
    )
    await update.message.reply_text(response)
    return ConversationHandler.END


async def remove_stocks(update: Update, context: CallbackContext):
    stocks = [s.strip() for s in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "delete_stocks", stocks)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def add_stocks(update: Update, context: CallbackContext):
    stocks = [s.strip() for s in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "add_stocks", stocks)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def remove_news(update: Update, context: CallbackContext):
    chosen_news = [n.strip() for n in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "delete_news", chosen_news)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def add_news(update: Update, context: CallbackContext):
    chosen_news = [n.strip() for n in update.message.text.split(",")]
    response = api_client.put_preference(update.effective_user.id, "add_news", chosen_news)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def process_preference_button_click(update: Update, context: CallbackContext):
    """Bearbeitet die Button-Klicks für das Ändern der Präferenzen."""
    query = update.callback_query
    await query.answer()

    if query.data == "course":
        return await ask_user_for_preference_change(update, context, COURSE_UPDATE, "Was ist dein neuer Kurs?")
    elif query.data == "cafeteria":
        return await ask_user_for_preference_change(update, context, CAFETERIA_UPDATE, "Was ist deine neue Mensa?")
    elif query.data == "city":
        return await ask_user_for_preference_change(update, context, CITY_UPDATE, "Was ist dein neuer Wohnort?")
    elif query.data == "transport":
        return await ask_user_for_preference_change(update, context, TRANSPORT_UPDATE, "Was ist dein neuer Transport?")
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
        return await ask_user_for_preference_change(
            update, context, STOCKS_DELETE, "Welche Aktien möchtest du entfernen?"
        )
    elif query.data == "stocks_add":
        return await ask_user_for_preference_change(
            update, context, STOCKS_ADD, "Welche Aktien möchtest du hinzufügen?"
        )
    elif query.data == "news_delete":
        return await ask_user_for_preference_change(
            update, context, NEWS_DELETE, "Welche Nachrichtenthemen möchtest du entfernen?"
        )
    elif query.data == "news_add":
        return await ask_user_for_preference_change(
            update, context, NEWS_ADD, "Welche Nachrichtenthemen möchtest du hinzufügen?"
        )

def configure_conversation_handlers(application):
    init_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_initialization)],
        states={
            COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_course)],
            CAFETERIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_cafeteria)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_city)],
            TRANSPORT: [CallbackQueryHandler(initialize_transport, pattern=r"^transport:")],
            STOCKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, initialize_stocks)],
            NEWS: [CallbackQueryHandler(initialize_news, pattern=r"^news:")],
        },
        fallbacks=[]
    )

    update_handler = ConversationHandler(
        entry_points=[CommandHandler("changepref", start_change_preferences)],
        states={
            BUTTON: [CallbackQueryHandler(process_preference_button_click)],
            COURSE_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_course)],
            CAFETERIA_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_cafeteria)],
            CITY_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_city)],
            TRANSPORT_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_transport)],
            STOCKS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_stocks)],
            STOCKS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_stocks)],
            NEWS_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_news)],
            NEWS_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_news)],
        },
        fallbacks=[]
    )

    application.add_handler(init_handler)
    application.add_handler(update_handler)
    application.add_handler(CommandHandler("showpref", show_preferences))
