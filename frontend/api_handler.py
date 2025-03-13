import requests

'''
user_data = {
            "username": "existinguser",
            "course": "Math",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Car",
            "stocks": ["Tesla"],
            "news": ["Reuters"]
        }
'''

def get_answer(message: str) -> str:
    url = "http://api:8000/answer"
    params = {"message": message}  # Query-Parameter

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return(response.json()["answer"])
        else:
            return(response.status_code + ": " + "Fehler bei der Anfrage an die API.")
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
            return(response.status_code + ": " + "Fehler bei der Azeige der Präferenzen.", "error")
    except:
        return "Ich kann gerade deine Präferenzen nicht abrufen.", "error"

def post_preferences(user_id: int, preferences: dict) -> str:
    url = "http://api:8000/preferences/init"
    data = {
        "username": str(user_id),
        "course": preferences["kurs"],
        "cafeteria": preferences["mensa"],
        "city": preferences["wohnort"],
        "preferred_transport_medium": preferences["transport"],
        "stocks": preferences["aktien"],
        "news": preferences["news"]
    }

    try:
        response = requests.post(url, json=data)

        if response.status_code == 200:
            return "Deine Präferenzen wurden erfolgreich gespeichert."
        else:
            return(response.status_code + ": " + "Fehler bei der Anfrage an die API.")
    except:
        return "Du hast deine Präferenzen anscheinend schon initialisiert."

def update_preference(user_id: int, preference: str, new_value: str) -> str:
    url = "http://api:8000/preferences/update"
    data = {
        "username": str(user_id),
        "preference": preference,
        "new_value": new_value
    }

    try:
        response = requests.put(url, json=data)

        if response.status_code == 200:
            return "Deine Präferenz wurde erfolgreich geändert."
        else:
            return(response.status_code + ": " + "Fehler bei der Anfrage an die API.")
    except:
        return "Ich kann gerade deine Präferenz nicht ändern."