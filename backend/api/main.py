from fastapi import FastAPI, Query, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.AnswerProcessor import AnswerProcessor
from api.models import User, UserUpdate
from api.preference_endpoints import init_user_preferences, get_user_preferences, update_user_preferences

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/answer")
async def get_answer(message: str = Query(..., min_length=1), user_id : str = Query(..., min_length=1)):
    answer_processor = AnswerProcessor()
    return await answer_processor.get_answer(message, user_id)

@app.get("/proactivity")
def get_proactivity():
    return {"proactivity": "proactivity"}

@app.post("/preferences/init")
async def init_preferences(user: User):
    return await init_user_preferences(user)

@app.get("/preferences/{username}", response_model=User)
async def get_preferences(username: str) -> Optional[User]:
    return await get_user_preferences(username)

@app.put("/preferences/{username}")
async def update_preferences(username: str, user: UserUpdate):
    return await update_user_preferences(username, user)