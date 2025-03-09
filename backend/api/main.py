from fastapi import FastAPI, Query
import asyncpg
from typing import Dict

app = FastAPI()

DATABASE_URL = "postgresql://user:password@preferences_db:5432/preferences_db"

async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

@app.get("/answer")
def get_answer(message: str = Query(..., min_length=1)):
    #answer = llm.getAnswer()
    answer = "I am a chatbot and this is my answer to your question: " + message
    return {"answer": answer}

@app.post("/preferences/init")
def init_preferences():
    return {"Hello": "World"}

@app.get("/preferences/{username}")
async def get_preferences(username: str) -> Dict:
    conn = await get_db_connection()
    
    query = """
    SELECT 
        u.username, 
        u.course, 
        u.cafeteria, 
        u.city, 
        u.preferred_transport_medium,
        STRING_AGG(s.stock_name, ', ') AS stocks,
        STRING_AGG(n.news_name, ', ') AS news
    FROM users u
    LEFT JOIN user_stocks us ON u.u_id = us.u_id
    LEFT JOIN stocks s ON us.s_id = s.s_id
    LEFT JOIN user_news un ON u.u_id = un.u_id
    LEFT JOIN news n ON un.n_id = n.n_id
    WHERE u.username = $1
    GROUP BY u.u_id;
    """
    
    result = await conn.fetchrow(query, username)

    await conn.close()
    
    if result:
        return {
            "username": result["username"],
            "course": result["course"],
            "cafeteria": result["cafeteria"],
            "city": result["city"],
            "preferred_transport_medium": result["preferred_transport_medium"],
            "stocks": result["stocks"].split(",") if result["stocks"] else [],
            "news": result["news"].split(",") if result["news"] else [],
        }
    else:
        return {"message": "User not found"}

@app.put("/preferences/{username}")
def update_preferences():
    return {"Hello": "World"}