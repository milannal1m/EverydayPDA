# Define conversation flow states (für die Einrichtung)
(
    CAFETERIA, 
    CITY, 
    TRANSPORT, 
    STOCKS, 
    NEWS
) = range(5)

# Zustände für Updates
(
    BUTTON,
    CAFETERIA_UPDATE,
    CITY_UPDATE,
    TRANSPORT_UPDATE,
    STOCKS_DELETE,
    STOCKS_ADD,
    NEWS_DELETE,
    NEWS_ADD
) = range(5, 13)

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