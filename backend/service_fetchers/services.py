import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim # INSTALLIEREN!!!
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")

# 1. Aktien (Twelve Data)
def get_stock_price(symbols):
    stocks = {}

    for symbol in symbols:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url)
        stock = response.json()

        url = f"https://api.twelvedata.com/quote?symbol={symbol}&interval=1h&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url)
        stock.update(response.json())

        # Filters out the stocks symbol, price and datetime
        stocks[symbol] = {
            "price": stock.get("values", [{}])[0].get("close"),
            "datetime": stock.get("values", [{}])[0].get("datetime"),
            "changeFrom1hour": stock.get("change")
        }

    return stocks


# 2. Nachrichten (NewsAPI)
# Categories: business, entertainment, general, health, science, sports, technology
def get_news(categories):
    news = {}

    for category in categories:
        url = f"https://newsapi.org/v2/top-headlines?category={category}&pageSize=1&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        articles = response.json().get("articles", [])

        # Adds the category to the news dictionary
        if category not in news:
            news[category] = []

        # Filters out the articles title and url
        for article in articles:
            news[category].append({ 
                "title": article.get("title"),
                "source": article.get("url"),
                "publishedAt": article.get("publishedAt"),
            })
    return news


# 3. Wetter (WeatherAPI)
def get_weather(cities):
    weatherCities = {}

    for city in cities:
        url = f"http://api.weatherapi.com/v1/current.json&/forecast.json ?key={WEATHER_API_KEY}&q={city}"
        response = requests.get(url)
        condition = response.json()

        # Filters out the locations name, temperature and feelslike temperature
        weatherCities[city] = {
                "temperature": condition.get("current", {}).get("temp_c"),
                "feelslike": condition.get("current", {}).get("feelslike_c"),
                "max_temp": condition.get("forecast", {}).get("forecastday", [{}])[0].get("day", {}).get("maxtemp_c"),
                "min_temp": condition.get("forecast", {}).get("forecastday", [{}])[0].get("day", {}).get("mintemp_c"),
            } 
               
    return weatherCities







'''
# 4. Cafeteria (CafeteriaAPI)
def get_cafeteria_menu(cafeteria_name):
    url = f"https://api.cafeteriaapi.com/v1/menus?cafeteria={cafeteria_name}"
    response = requests.get(url)
    return response.json()

    
# 5. Stundenplan (StundenplanAPI)
def get_timetable(course_name):
    url = f"https://api.stundenplanapi.com/v1/timetable?course={course_name}"
    response = requests.get(url)
    return response.json()
'''






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

    location = city
    limit=5

    url = "https://engine.hotellook.com/api/v2/cache.json"
    params = {
        "location": location,
        "currency": "eur",
        "checkIn": check_in,
        "checkOut": check_out,
        "limit": limit
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"error": f"API-Fehler: {response.status_code} - {response.text}"}

    data = response.json()
    hotels = []

    for item in data:
        hotels.append({
            "name": item.get("hotelName", "Unbekannt"),
            "price": item.get("priceFrom", "k.A."),
            "stars": item.get("stars", "k.A.")
        })

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
    print("📈 Aktienkurs:", get_stock_price(["AAL", "GOOGL"]))
    print("📰 Nachrichten:", get_news(["business"]))
    print("🌤️ Wetter:", get_weather(["Stuttgart"]))
    #print("🍽️ Mensa:", get_cafeteria_menu("Mensa Stuttgart"))
    #print("📅 Stundenplan:", get_timetable("IN22"))
    print("🚗 Routenzeit:", get_travel_time("driving-car", "Stuttgart", "Hamburg"))
    print("🏨 Hotels:", get_hotels("Stuttgart", "2025-05-10", "2025-05-12"))
    print("✈️ Flugstatus:", get_flights("Stuttgart", "London", "2025-05-10", "2025-05-15"))