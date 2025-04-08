import requests


def get_answer(message: str, user_id: int) -> str:
    url = "http://api:8000/answer"
    params = {"message": message,
              "user_id": str(user_id)}  # Query-Parameter

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return(response.json()["response"])
        else:
            return f"{response.status_code}: Fehler bei der Anfrage an die API."
    except:
        return "Ich kann mich gerade nicht mit der API verbinden."
    

def get_morning_message(user_id: int) -> str:
    url = "http://api:8000/morning"
    params = {"user_id": str(user_id)}  # Query-Parameter
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return(response.json()["response"])
        else:
            return f"{response.status_code}: Fehler bei der Anfrage an die API."
    except:
        return "Ich kann mich gerade nicht mit der API verbinden."


def get_preferences(user_id: int) -> tuple:
    url = "http://api:8000/preferences/" + str(user_id)

    try:
        response = requests.get(url)

        if response.status_code == 200:
            summary = (f"Hier ist deine Übersicht:\n\n"
            f"📚 Kurs: {response.json()['course']}\n"
            f"🍽️ Mensa: {response.json()['cafeteria']}\n"
            f"🏠 Wohnort: {response.json()['city']}\n"
            f"🚆 Transport: {response.json()['preferred_transport_medium']}\n"
            f"📈 Lieblingsaktien: {', '.join(response.json()['stocks'])}\n"
            f"📰 Nachrichtenquellen: {', '.join(response.json()['news'])}")
            return(summary, "success")
        else:
            return(f"{response.status_code}: Fehler bei der Anzeige der Präferenzen.", "error")
    except:
        return "Ich kann gerade deine Präferenzen nicht abrufen.", "error"


def post_preferences(user_id: int, preferences: dict) -> str:
    url = "http://api:8000/preferences/init"
    data = {
        "username": str(user_id),
        "course": preferences.get("course", ""),  # Verhindert KeyError
        "cafeteria": preferences.get("cafeteria", ""),
        "city": preferences.get("city", ""),
        "preferred_transport_medium": preferences.get("transport", ""),
        "stocks": preferences.get("stocks", []),
        "news": preferences.get("news", [])
    }

    try:
        response = requests.post(url, json=data)

        if response.status_code == 200:
            return "Deine Präferenzen wurden erfolgreich gespeichert."
        else:
            return f"{response.status_code}: Fehler bei der Anfrage an die API."
    except:
        return "Du hast deine Präferenzen anscheinend schon initialisiert."


def put_preference(user_id: int, key: str, new_value):
    url = f"http://api:8000/preferences/{user_id}"
    
    try:
        # Aktuelle Präferenzen abrufen
        response = requests.get(url)
        
        if response.status_code != 200:
            return f"Fehler beim Abrufen der aktuellen Präferenzen: {response.status_code}"

        current_data = response.json()

        extra_keys = ["delete_stocks", "add_stocks", "delete_news", "add_news"]

        # Überprüfen, ob der Schlüssel existiert
        if key not in current_data and key not in extra_keys:
            return f"Ungültige Präferenz: {key}"

        # Nur den gewünschten Key aktualisieren
        current_data[key] = new_value

        # Aktualisierte Präferenzen senden
        put_response = requests.put(url, json=current_data)

        if put_response.status_code == 200:
            return f"Deine Präferenz wurde erfolgreich aktualisiert."
        else:
            return f"Fehler bei der Aktualisierung: {put_response.status_code}"

    except requests.RequestException:
        return "Ich kann gerade deine Präferenz nicht ändern."