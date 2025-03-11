import requests

def get_answer(message: str) -> str:
    url = "http://localhost:8000/answer"
    params = {"message": message}  # Query-Parameter

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return(response.json())
    else:
        return(response.status_code)
