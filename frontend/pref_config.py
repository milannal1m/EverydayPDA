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