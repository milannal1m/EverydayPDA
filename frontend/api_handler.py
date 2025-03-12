import requests

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
