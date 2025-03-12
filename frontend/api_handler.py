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