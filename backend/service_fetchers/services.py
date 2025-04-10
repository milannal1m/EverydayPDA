import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import time
import difflib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")

# 1. Stocks (Twelve Data)
#
# Parameters:
# - stock_names (list of str): Company names (e.g., ["Apple", "Google"])
#
# Returns:
# - dict: Maps each company name to a dict with:
#     - "price" (str): Latest stock price
#     - "timestamp" (str): Datetime of the latest price
#     - "changeFrom1hour" (str): Price change from one hour ago
def get_stock_price(stock_names):
    stocks = {}

    for stock_name in stock_names:
        # Lookup ticker symbol by company name
        search_url = (
            f"https://api.twelvedata.com/symbol_search?symbol={stock_name}&apikey={TWELVE_DATA_API_KEY}"
        )
        response = requests.get(search_url)
        data = response.json()

        if not data.get("data"):
            continue  # Skip if no match found

        symbol = data["data"][0].get("symbol")

        print(f"Symbol: {symbol}")

        # Get latest 1min time series
        url = (
            f"https://api.twelvedata.com/time_series"
            f"?symbol={symbol}&interval=1min&apikey={TWELVE_DATA_API_KEY}"
        )
        response = requests.get(url)
        stock = response.json()

        # Get quote with hourly change
        url = (
            f"https://api.twelvedata.com/quote"
            f"?symbol={symbol}&interval=1h&apikey={TWELVE_DATA_API_KEY}"
        )
        response = requests.get(url)
        stock.update(response.json())

        if response.json().get("code") == 400:
            continue
        else:
            # Filters price, timestamp and hourly change
            stocks[stock_name] = {
                "price": stock.get("values", [{}])[0].get("close"),
                "timestamp": stock.get("values", [{}])[0].get("datetime"),
                "changeFrom1hour": stock.get("change"),
            }

    return stocks


# 2. News (NewsAPI)
#
# Parameters:
# - categories (list of str): News categories to query. Must be one or more of:
#     "business", "entertainment", "general", "health", "science", "sports", "technology"
#
# Returns:
# - dict: Maps each category to a list of articles, where each article contains:
#     - "title" (str): Headline of the article
#     - "source" (str): URL of the article
#     - "publishedAt" (str): Publication datetime in ISO format
def get_news(categories):
    news = {}

    for category in categories:
        url = (
            f"https://newsapi.org/v2/top-headlines"
            f"?category={category}&pageSize=1&apiKey={NEWS_API_KEY}"
        )
        response = requests.get(url)
        articles = response.json().get("articles", [])

        if response.json().get("totalResults") == 0:
            continue

        if category not in news:
            news[category] = []

        # Extracts article title, URL, and publication date
        for article in articles:
            news[category].append({
                "title": article.get("title"),
                "source": article.get("url"),
                "publishedAt": article.get("publishedAt"),
            })

    return news


# 3. Weather (WeatherAPI)
#
# Parameters:
# - cities (list of str): List of city names (e.g., ["Berlin", "Paris", "New York"])
#
# Returns:
# - dict: Maps each city to a dict with:
#     - "temperature" (float): Current temperature in °C
#     - "feelslike" (float): Feels-like temperature in °C
#     - "max_temp" (float): Forecasted max temperature for the day in °C
#     - "min_temp" (float): Forecasted min temperature for the day in °C
def get_weather(cities):
    weather_cities = {}

    for city in cities:
        url = (
            f"http://api.weatherapi.com/v1/forecast.json"
            f"?key={WEATHER_API_KEY}&q={city}"
        )
        response = requests.get(url)
        condition = response.json()

        if condition.get("error", {}).get("message") == "No matching location found.":
            continue

        weather_cities[city] = {
            "temperature": condition.get("current", {}).get("temp_c"),
            "feelslike": condition.get("current", {}).get("feelslike_c"),
            "max_temp": condition
                .get("forecast", {})
                .get("forecastday", [{}])[0]
                .get("day", {})
                .get("maxtemp_c"),
            "min_temp": condition
                .get("forecast", {})
                .get("forecastday", [{}])[0]
                .get("day", {})
                .get("mintemp_c"),
        }

    return weather_cities



# 4. Cafeteria (CafeteriaAPI)
def get_canteen_id_by_fuzzy_name(name_query, min_ratio=0.6):
    url = "https://openmensa.org/api/v2/canteens"
    page = 1
    candidates = {}

    while True:
        response = requests.get(url, params={"page": page})
        if response.status_code != 200:
            return None

        canteens = response.json()
        if not canteens:
            break

        print(canteens)

        for canteen in canteens:
            full_name = f"{canteen.get('name', '')} {canteen.get('city', '')}"
            candidates[full_name] = canteen["id"]

        page += 1

    # Fuzzy Match
    matches = difflib.get_close_matches(name_query, candidates.keys(), n=1, cutoff=min_ratio)
    if not matches:
        return None

    return candidates[matches[0]]

def get_mensa_info(canteen_id):

    date = time.strftime("%Y-%m-%d") # heute Datum im Format YYYY-MM-DD
    #canteen_id = get_canteen_id_by_fuzzy_name(canteen_name)

    print(f"Kantinen-ID:", canteen_id) # canteen_id = 1202  # ID der Mensa Central Stuttgart (Beispiel)
    
    if not canteen_id:
        return {"error": "Kantine nicht gefunden."}

    meals = {}

    url = f"https://openmensa.org/api/v2/canteens/{canteen_id}/days/{date}/meals"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": f"Fehler beim Abrufen: {response.status_code}"}

    meal_data = response.json()

    for meal in meal_data:
        meals[meal.get("name")] = {
            "category": meal.get("category"),
            "price": meal.get("prices", {}).get("students"),
        }

    return meals


    
#5. Stundenplan (StundenplanAPI)
def get_rapla_scedule(user_id, semester):
    url = f"https://rapla.dhbw.de/rapla/file=6Q0QSbNtpyeYPKQhnGFTaEN6AggaPdGgCFyhd5ANmjydX8WyDjUfLBh4YjDgat2dJd8as6Az5GGmQilBwJydDTQpeHfV6bTghpX2dlRU6RU5QsAKr6ARjgRj_BxZmmhVA3Tk_bSK4acN3oO7a7PkNAHTfszb0OA4_JMp8zdoYDY/user=inf22168@lehre.dhbw-stuttgart.de/day=today"
    response = requests.get(url)
    
    return response.json()



# 6. Wegezeitberechnung (OpenRouteService)
# Transport_Medium: "driving-car", "driving-hgv", "cycling-regular", "cycling-road", "cycling-mountain", "cycling-electric", "foot-walking", "foot-hiking", "wheelchair"
def geocode_location(place):
    geolocator = Nominatim(user_agent="route_planner")
    location = geolocator.geocode(place)
    time.sleep(1)  # Vermeidung von Rate-Limiting
    if location:
        return [location.longitude, location.latitude]
    return None

def get_travel_time(transport_medium, start_location, end_location):
    start_coords = geocode_location(start_location)
    end_coords = geocode_location(end_location)

    if not start_coords or not end_coords:
        return {"error": "Ungültiger Start- oder Zielort"}

    url = f"https://api.openrouteservice.org/v2/directions/{transport_medium}/geojson"
    headers = {
        "Authorization": OPENROUTE_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [start_coords, end_coords]
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    if "features" not in data:
        return {"error": data.get("error", response.text)}

    segment = data["features"][0]["properties"]["segments"][0]
    return {
        "distance_km": round(segment["distance"] / 1000, 2),
        "duration_min": round(segment["duration"] / 60, 2)
    }


# 7. Hotelsuche (Hotellook)
def get_hotels(city, check_in, check_out):
    url = "https://engine.hotellook.com/api/v2/cache.json"
    params = {
        "location": city,
        "currency": "eur",
        "checkIn": check_in,
        "checkOut": check_out,
        "limit": 5
    }

    response = requests.get(url, params=params)
    hotel_data = response.json()

    # Fehlerprüfung, wenn hotel_data ein Fehlerobjekt ist
    if isinstance(hotel_data, dict) and hotel_data.get("errorCode") == 2:
        return {}

    hotels = {}
    for hotel in hotel_data:
        hotels[hotel.get("hotelName")] = {
            "price": hotel.get("priceFrom", "keine Angabe"),
            "stars": hotel.get("stars", "keine Angabe")
        }

    return hotels




# 8. Fluginformationen (AviationStack)
def get_iata_code(city_name):
    # API-Endpunkt für die Flughafensuche
    url = f"https://api.aviationstack.com/v1/airports"
    params = {
        "access_key": AVIATION_STACK_API_KEY,
        "city": city_name
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    if not data.get("data"):
        return None
    
    # Der erste Treffer (meistens der Hauptflughafen der Stadt)
    airport = data["data"][0]
    return airport.get("iata_code", None)

def get_flights(origin_city, destination_city, departure_date, return_date):
    max_results = 3
    origin_iata = get_iata_code(origin_city)
    destination_iata = get_iata_code(destination_city)
    
    if not origin_iata or not destination_iata:
        return {"error": "Ungültige Stadt/Flughafen eingegeben."}
    
    # API-Endpunkt für Fluginformationen
    url = "https://api.aviationstack.com/v1/flights"
    params = {
        "access_key": AVIATION_STACK_API_KEY,
        "departure_iata": origin_iata,     # IATA-Code des Abreiseorts
        "arrival_iata": destination_iata,  # IATA-Code des Zielorts
        "departure_date": departure_date,  # Format: "YYYY-MM-DD"
        "return_date": return_date         # Format: "YYYY-MM-DD" (optional)
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return {"error": f"API-Fehler: {response.status_code} - {response.text}"}

    data = response.json()
    if not data.get("data"):
        return {"error": "Keine Flüge gefunden."}

    flights = []
    for flight in data["data"][:max_results]:  # Nur die ersten 'max_results' Flüge
        flights.append({
            "flight_name": flight.get("flight", {}).get("iata", "Unbekannt"),
            "departure": flight.get("departure", {}).get("estimated", "k.A."),
            "arrival": flight.get("arrival", {}).get("estimated", "k.A."),
            "price": flight.get("price", {}).get("total", "k.A.")  # Falls verfügbar
        })

    return flights


# --- Testaufrufe ---
if __name__ == "__main__":
    print("📈 1: Aktienkurs:", get_stock_price(["Siemens AG"]))
    print("📰 2: Nachrichten:", get_news(["technology"]))
    print("🌤️ 3: Wetter:", get_weather(["Stuttgart"]))
    #print("🍽️ 4: Mensa:", get_mensa_info("mensa ludwigsburg, ludwigsburg", "2025-04-09"))
    #print("📅 5: Stundenplan:", get_rapla_scedule("doelker%40verwaltung.ba-stuttgart.de", "2025SS"))
    #print("🚗 6: Routenzeit:", get_travel_time("driving-car", "Stuttgart", "Hamburg"))
    print("🏨 7: Hotels:", get_hotels("Berlin", "2025-05-10", "2025-05-12"))
    #print("✈️ 8: Flugstatus:", get_flights("Stuttgart", "Hamburg", "2025-05-10", "2025-05-15"))