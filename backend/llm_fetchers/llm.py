import openai
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OpenAI API key not found. Please set it in the .env file.")
openai.api_key = OPENAI_API_KEY

app = FastAPI()
class MiddlewareRequest(BaseModel):
    user_input: str

def process_input_with_chatgpt(user_input: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}],
            max_tokens=200
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/middleware")
def middleware(data: MiddlewareRequest):
    processed_response = process_input_with_chatgpt(data.user_input)
    return {"response": processed_response}

@app.get("/answer")
def get_answer(message: str = Query(..., min_length=1)):
    answer = process_input_with_chatgpt(message)
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)