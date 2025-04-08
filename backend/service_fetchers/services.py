import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim # INSTALLIEREN!!!
import time

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
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

<<<<<<< HEAD
        url = f"https://api.twelvedata.com/quote?symbol={symbol}&interval=1week&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url)
        stock.update(response.json())

        # Filters out the stocks symbol, price and datetime
=======
        # Filters out the stocks, price and datetime
>>>>>>> 2078eedb66ead6ca89de026983f18b2dc9b8dd97
        stocks[symbol] = {
            "price": stock.get("values", [{}])[0].get("close"),
            "datetime": stock.get("values", [{}])[0].get("datetime"),
            "changeFromYesterday": stock.get("change")
        }

    return stocks

# 2. Nachrichten (NewsAPI)
#Themen: business entertainment general health science sports technology
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


# 7. Hotelsuche (Amadeus)
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token")

def get_city_code(city_name, token): # Ortsname → City Code (z.B. "Stuttgart" → "STR")
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    params = {
        "keyword": city_name,
        "subType": "CITY"
    }
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers, params=params)
    results = response.json().get("data", [])
    #print("City Code:", results) # Debug-Ausgabe
    if results:
        return results[0]["iataCode"]
    return None

def get_city_hotels(city_code, token):
    url = f"https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "cityCode": city_code,
        "radius": 20,
        "radiusUnit": "KM"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    hotel_ids = [hotel["hotelId"] for hotel in data.get("data", [])[:5]]  # max. 5 Hotels
    return hotel_ids

def get_hotels(city, check_in, check_out):
    token = get_amadeus_token()
    city_code = get_city_code(city, token)
    if not city_code:
        return {"error": "Ungültiger Ort"}

    hotel_ids = get_city_hotels(city_code, token)
    if not hotel_ids:
        return {"error": "Keine Hotels gefunden"}

    url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "hotelIds": ",".join(hotel_ids),
        "checkInDate": check_in,
        "checkOutDate": check_out,
        "adults": 1,
        "currency": "EUR"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return {"error": f"API-Fehler: {response.status_code} - {response.text}"}

    data = response.json()
    hotels = []
    for item in data.get("data", []):
        hotel_info = item.get("hotel", {})
        offer_info = item.get("offers", [{}])[0]
        price_info = offer_info.get("price", {})

        hotels.append({
            "name": hotel_info.get("name", "Unbekannt"),
            "price": price_info.get("total", "k.A."),
            "rating": hotel_info.get("rating", "k.A.")
        })

    return hotels

'''
# 8. Fluginformationen (AviationStack)
def get_flight_status(destination):
    url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATION_STACK_API_KEY}&arr_iata=STR"
    response = requests.get(url)
    return response.json()
'''
# --- Testaufrufe ---
if __name__ == "__main__":
    print("📈 Aktienkurs:", get_stock_price(["AAL", "GOOGL"]))
    print("📰 Nachrichten:", get_news(["Technology"]))
    print("🌤️ Wetter:", get_weather(["Stuttgart"]))
    print("🚗 Routenzeit:", get_travel_time("wheelchair", "Stuttgart", "Hamburg"))
    print("🏨 Hotels:", get_hotels("Berlin", "2025-05-10", "2025-05-12"))
    #print("✈️ Flugstatus:", get_flight_status())