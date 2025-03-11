import requests

API_KEYS = {
    "twelve_data": "744ee61677174f7ab67776bb4baafc05",
    "newsapi": "bb8f2a67e4c242b7b3a1fb3e7b6b475a",
    "weatherapi": "7bc3ed65f5e2488abf6110618251103",
    "openrouteservice": "5b3ce3597851110001cf624863ead55248df484badb5065125478f8e",
    "aviationstack": "b27a026e11342d17fc0e71aaedd3f7a7"
}

# Amadeus API-Zugangsdaten
AMADEUS_CLIENT_ID = "aVcbGLl41sdldL9oGFXwcJMGBSOCgjLI"
AMADEUS_CLIENT_SECRET = "4mR7LMoSL8R4VMa0"

# 1. Aktien (Twelve Data)
def get_stock_price(symbol="AAPL"):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&apikey={API_KEYS['twelve_data']}"
    response = requests.get(url)
    return response.json()

# 2. Nachrichten (NewsAPI)
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=5&apiKey={API_KEYS['newsapi']}"
    response = requests.get(url)
    return response.json()

# 3. Wetter (WeatherAPI)
def get_weather(city="Berlin"):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEYS['weatherapi']}&q={city}"
    response = requests.get(url)
    return response.json()

# 4. Wegezeitberechnung (OpenRouteService)
def get_route_time(start=[8.6821, 50.1109], end=[8.6298, 50.1095]):  # Koordinaten (Lon, Lat)
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": API_KEYS["openrouteservice"], "Content-Type": "application/json"}
    params = {"start": f"{start[0]},{start[1]}", "end": f"{end[0]},{end[1]}"}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 5. Amadeus: Access Token abrufen
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    token_data = response.json()
    return token_data.get("access_token")

# 6. Hotelsuche (Amadeus)
def get_hotels(city_code="STR"):
    token = get_amadeus_token()
    if not token:
        return {"error": "Fehler beim Abrufen des Tokens"}
    
    url = f"https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city?cityCode={city_code}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# 7. Fluginformationen (AviationStack)
def get_flight_status(flight_number="LH201"):
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEYS['aviationstack']}&flight_iata={flight_number}"
    response = requests.get(url)
    return response.json()

# --- Testaufrufe ---
if __name__ == "__main__":
    print("📈 Aktienkurs:", get_stock_price("AAPL"))
    print("📰 Nachrichten:", get_news())
    print("🌤️ Wetter:", get_weather("Berlin"))
    print("🚗 Routenzeit:", get_route_time())
    print("🏨 Hotels:", get_hotels("STR"))
    print("✈️ Flugstatus:", get_flight_status("LH201"))
