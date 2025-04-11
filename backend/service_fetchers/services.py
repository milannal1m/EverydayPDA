import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from datetime import datetime
import time
import difflib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
X_RAPLA_API_KEY = os.getenv("X_RAPLA_API_KEY")

# Helper-function to check if a date is valid and convert it to the format YYYY-MM-DD
def is_valid_date(date_string):
    try:
        # Checks if date is in format YYYY-MM-DD
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string

    except ValueError:
        try:
            # Checks if date is in format DD.MM.YYYY
            parsed_date = datetime.strptime(date_string, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")

        except ValueError:
            # If Year is missing, append the current year
            current_year = datetime.now().year
            date_with_year = f"{date_string}{current_year}"
            parsed_date = datetime.strptime(date_with_year, "%d.%m.%Y")
            return parsed_date.strftime("%Y-%m-%d")
        

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
def get_news(news_topics):
    news = {}

    for news_topic in news_topics:
        url = (
            f"https://newsapi.org/v2/top-headlines"
            f"?category={news_topic}&pageSize=1&apiKey={NEWS_API_KEY}"
        )
        response = requests.get(url)
        articles = response.json().get("articles", [])

        if response.json().get("totalResults") == 0:
            continue

        if news_topic not in news:
            news[news_topic] = []

        # Extracts article title, URL, and publication date
        for article in articles:
            news[news_topic].append({
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


# 4. Canteen Info (OpenMensa API)
#
# Parameters:
# - canteen_name (list of str): List of Approximate names of canteens (e.g., ["Mensa Central", "Mensa Hohenheim"])
#
# Returns:
# - dict: Maps each meal name to:
#     - "category" (str): Meal category (e.g., "Vegetarian", "Main dish")
#     - "price" (float or None): Price for students in EUR
#   Returns error message if the canteen is not found or request fails.
def get_canteen_info(canteen_names):
    min_ratio = 0.6

    # Helper function for normalizing names (lowercase and removing special characters)
    def normalize_name(name):
        name = name.lower()
        # Remove any special characters or extra spaces
        name = name.replace(",", "").replace("(", "").replace(")", "")
        return name.strip()

    # Weighted matching function that prioritizes certain keywords
    def weighted_match(name, candidates, min_ratio):
        best_match = None
        highest_score = 0

        for candidate_name, canteen_id in candidates.items():
            # Get base score using normal matching
            score = difflib.SequenceMatcher(None, name, candidate_name).ratio()

            # Weight the score higher if key terms like "Mensa Central" are present
            if "mensa central" in name and "mensa central" in candidate_name:
                score += 0.2  # Add bonus for matching key term "Mensa Central"

            # Update if we find a better match
            if score > highest_score and score >= min_ratio:
                best_match = canteen_id
                highest_score = score

        return best_match

    url = "https://openmensa.org/api/v2/canteens"
    page = 1
    candidates = {}

    while True:
        response = requests.get(url, params={"page": page})
        if response.status_code != 200:
            return {"error": f"Fehler beim Laden der Kantinen: {response.status_code}"}

        canteens = response.json()
        if not canteens:
            break

        # Process each canteen
        for canteen in canteens:
            full_name = f"{canteen.get('name', '')} {canteen.get('city', '')}"
            normalized_name = normalize_name(full_name)
            candidates[normalized_name] = canteen["id"]

        page += 1

    # Prepare the result for each canteen name in the input list
    all_menus = {}

    for canteen_name in canteen_names:
        normalized_input = normalize_name(canteen_name)

        # Find the best match based on the weighted matching
        canteen_id = weighted_match(normalized_input, candidates, min_ratio)
        if not canteen_id:
            all_menus[canteen_name] = {"error": "Kantine nicht gefunden."}
            continue

        date = time.strftime("%Y-%m-%d")  # Todays date with format YYYY-MM-DD

        url = f"https://openmensa.org/api/v2/canteens/{canteen_id}/days/{date}/meals"
        response = requests.get(url)

        if response.status_code != 200:
            all_menus[canteen_name] = {"error": f"Fehler beim Abrufen: {response.status_code}"}
            continue

        meals = {}
        for idx, meal in enumerate(response.json()):
            if idx >= 3:  # Stop after the first 3 meals
                break
            meals[meal.get("name")] = {
                "category": meal.get("category"),
                "price": meal.get("prices", {}).get("students"),
            }

        all_menus[canteen_name] = meals

    return all_menus


# 5. Schedule (Rapla API)
#
# Parameters:
# - dates (list of str): List of dates (in "YYYY-MM-DD" format) for which to retrieve events
#
# Returns:
# - dict: Maps each event summary to a dictionary containing:
#     - "start" (str): Event start time in "HH:MM" format
#     - "end" (str): Event end time in "HH:MM" format
#     - "location" (str): Event location
def get_rapla_schedule(dates):
    url = (
        "http://rapla.satoqz.net/rapla/internal_calendar?"
        "key=6Q0QSbNtpyeYPKQhnGFTaEN6AggaPdGgCFyhd5ANmjydX8WyDjUfLBh4YjDgat2dJd8as6Az5GGmQilBwJydDTQpeHfV6bTghpX2dlRU6RU5QsAKr6ARjgRj_BxZmmhVA3Tk_bSK4acN3oO7a7PkNAHTfszb0OA4_JMp8zdoYDY"
        "&salt=648736798"
    )
    response = requests.get(url)

    ics_file = response.text

    current_event = {}
    events = {}

    # Iterates through all lines of the given ICS file
    for date in dates:
        date = is_valid_date(date)
        for line in ics_file.splitlines():
            line = line.strip()

            if line.startswith("BEGIN:VEVENT"):
                current_event = {}

            elif line.startswith("DTSTAMP:"):
                timestamp = line.replace("DTSTAMP:", "").strip().split("T")[0]
                current_event["timestamp"] = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:]}"

            elif line.startswith("SUMMARY:"):
                current_event["summary"] = line.replace("SUMMARY:", "").strip()

            elif line.startswith("DTSTART;TZID=Europe/Berlin:"):
                start_time = line.replace("DTSTART;TZID=Europe/Berlin:", "").strip().split("T")[1]
                current_event["start"] = f"{start_time[:2]}:{start_time[4:6]}"

            elif line.startswith("DTEND;TZID=Europe/Berlin:"):
                end_time = line.replace("DTEND;TZID=Europe/Berlin:", "").strip().split("T")[1]
                current_event["end"] = f"{end_time[:2]}:{end_time[4:6]}"

            elif line.startswith("LOCATION:"):
                current_event["location"] = line.replace("LOCATION:", "").strip()

            elif line.startswith("END:VEVENT"):
                if "summary" in current_event and current_event["timestamp"] == date:
                    events[current_event["summary"]] = {
                        "start": current_event.get("start"),
                        "end": current_event.get("end"),
                        "location": current_event.get("location"),
                    }

    return events


# 6. Travel Time (OpenRouteService)
#
# Parameters:
# - transport_medium (list of str): A list containing one of the following:
#   "driving-car", "driving-hgv", "cycling-regular", "cycling-road", "cycling-mountain", "cycling-electric", "foot-walking", "foot-hiking", "wheelchair"
# - start_location (list of str): A list containing the start location name (e.g., "Stuttgart")
# - end_location (list of str): A list containing the destination name (e.g., "Hamburg")
#
# Returns:
# - dict: If successful:
#     - "distance_km" (float): Distance in kilometers
#     - "duration_min" (float): Duration in minutes
#   If error:
#     - "error" (str): Error message
def get_travel_info(transport_medium, start_location, end_location):
    def geocode_location(place):
        geolocator = Nominatim(user_agent="route_planner")
        location = geolocator.geocode(place)
        time.sleep(1)
        if location:
            return [location.longitude, location.latitude]
        return None

    # Use the first element of each list for the calculation
    transport = transport_medium[0]
    start_coords = geocode_location(start_location[0])
    end_coords = geocode_location(end_location[0])

    if not start_coords or not end_coords:
        return {"error": "Ungültiger Start- oder Zielort"}

    url = f"https://api.openrouteservice.org/v2/directions/{transport}/geojson"
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
    travel_info = {
        "distance_km": round(segment["distance"] / 1000, 2),
        "duration_min": round(segment["duration"] / 60, 2)
    }

    return travel_info


# 7. Hotel Search (Hotellook)
#
# Parameters:
# - city_list (list): City name as first element, e.g. ["Berlin"]
# - checkin_list (list): Check-in date (YYYY-MM-DD, DD.MM.YYYY, DD.MM.YY, DD.MM.), e.g. ["2025-05-10"]
# - checkout_list (list): Check-out date (YYYY-MM-DD, DD.MM.YYYY, DD.MM.YY, DD.MM.), e.g. ["2025-05-12"]
#
# Returns:
# - dict: hotels – contains hotel name as key and:
#     - "price" (float or str): Price per night or "keine Angabe"
#     - "stars" (int or str): Star rating or "keine Angabe"
def get_hotels(city_list, checkin_list, checkout_list):
    city = city_list[0]
    
    # Changing dates into correct format
    check_in = is_valid_date(checkin_list[0])
    check_out = is_valid_date(checkout_list[0])

    url = "https://engine.hotellook.com/api/v2/cache.json"
    params = {
        "location": city,
        "currency": "eur",
        "checkIn": check_in,
        "checkOut": check_out,
        "limit": 3
    }

    response = requests.get(url, params=params)
    hotel_data = response.json()

    if isinstance(hotel_data, dict) and hotel_data.get("errorCode") == 2:
        return {}

    hotels = {}
    for hotel in hotel_data:
        hotels[hotel.get("hotelName")] = {
            "price": hotel.get("priceFrom", "keine Angabe"),
            "stars": hotel.get("stars", "keine Angabe")
        }

    return hotels


# 8. Flight Search (Amadeus API)
#
# Parameters:
#   - origin_city (list[str]): Departure city, e.g. ["Stuttgart"]
#   - destination_city (list[str]): Arrival city, e.g. ["Hamburg"]
#   - departure_date (list[str]): Departure date, format "YYYY-MM-DD", or "DD.MM.YYYY", or "DD.MM.YY"
#   - return_date (list[str], optional): Return date, format "YYYY-MM-DD", or "DD.MM.YYYY", or "DD.MM.YY"
#
# Returns:
#   - dict: Contains flight details (max. 3 flights) or error message
def get_flights(origin_city, destination_city, departure_date, return_date=None):
    def get_access_token(): # Obtain OAuth2 token from Amadeus API.
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_CLIENT_ID,
            "client_secret": AMADEUS_CLIENT_SECRET
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")

    def city_to_iata(city_name, token): # Resolve city name to IATA code via Amadeus location API.
        url = "https://test.api.amadeus.com/v1/reference-data/locations"
        params = {"keyword": city_name, "subType": "AIRPORT"}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            raise ValueError(f"No IATA code found for city: {city_name}")

        return data["data"][0]["iataCode"]

    try:
        token = get_access_token()
        origin_iata = city_to_iata(origin_city[0], token)
        destination_iata = city_to_iata(destination_city[0], token)
    except Exception as e:
        return {"error": str(e)}

    # Umwandlung der Datumsangaben ins richtige Format
    departure_date = is_valid_date(departure_date[0])
    if return_date:
        return_date = is_valid_date(return_date[0])

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    params = {
        "originLocationCode": origin_iata,
        "destinationLocationCode": destination_iata,
        "departureDate": departure_date,
        "adults": 1,
        "currencyCode": "EUR",
        "max": 3
    }

    if return_date:
        params["returnDate"] = return_date

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {
            "error": f"API request failed: {response.status_code}",
            "details": response.text
        }

    data = response.json()
    if not data.get("data"):
        return {"error": "No flight data available."}

    flights = []
    for flight in data["data"][:3]:
        segment = flight["itineraries"][0]["segments"][0]
        flights.append({
            "flight_number": segment["carrierCode"],
            "airline": segment["carrierCode"],
            "departure": segment["departure"]["at"],
            "arrival": segment["arrival"]["at"],
            "price": flight["price"]["grandTotal"]
        })

    return {"flights": flights}


# --- Testaufrufe ---
if __name__ == "__main__":
    print("📈 1: Aktienkurs:", get_stock_price(["Siemens AG"]))
    print("📰 2: Nachrichten:", get_news(["technology"]))
    print("🌤️ 3: Wetter:", get_weather(["Stuttgart"]))
    print("🍽️ 4: Mensa:", get_canteen_info(["Mensa Central"]))
    print("📅 5: Stundenplan:", get_rapla_schedule(["15.04."]))
    print("🚗 6: Routenzeit:", get_travel_info(["driving-car"], ["Stuttgart"], ["Hamburg"]))
    print("🏨 7: Hotels:", get_hotels(["Berlin"], ["20.05."], ["24.05."]))
    print("✈️ 8: Flugstatus:", get_flights(["Stuttgart"], ["Houston"], ["11.05."], ["27.05.2025"]))