from fastapi import FastAPI, Query, HTTPException
import asyncpg
from typing import Dict, List, Optional
from pydantic import BaseModel 

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

class User(BaseModel):
    username: str
    course: str
    cafeteria: str
    city: str
    preferred_transport_medium: str
    stocks: Optional[List[str]] = []
    news: Optional[List[str]] = []

@app.post("/preferences/init")
async def init_preferences(user: User):
    conn = await get_db_connection()
    async with (await conn.transaction()):
        check_query = "SELECT COUNT(*) FROM users WHERE username = $1"
        existing = await conn.fetchval(check_query, user.username)

        if existing > 0:
            await conn.close()
            raise HTTPException(status_code=400, detail="User already exists")

        insert_user_query = """
        INSERT INTO users (username, course, cafeteria, city, preferred_transport_medium)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING u_id
        """
        user_id = await conn.fetchval(insert_user_query, user.username, user.course, user.cafeteria, user.city, user.preferred_transport_medium)

        if user.stocks:
            for stock_name in user.stocks:
                stock_id = await conn.fetchval("SELECT s_id FROM stocks WHERE stock_name = $1", stock_name)
                if not stock_id:
                    stock_id = await conn.fetchval("INSERT INTO stocks (stock_name) VALUES ($1) RETURNING s_id", stock_name)
                
                await conn.execute("INSERT INTO user_stocks (u_id, s_id) VALUES ($1, $2)", user_id, stock_id)

        if user.news:
            for news_name in user.news:
                news_id = await conn.fetchval("SELECT n_id FROM news WHERE news_name = $1", news_name)
                if not news_id:
                    news_id = await conn.fetchval("INSERT INTO news (news_name) VALUES ($1) RETURNING n_id", news_name)

                await conn.execute("INSERT INTO user_news (u_id, n_id) VALUES ($1, $2)", user_id, news_id)

    await conn.close()
    return {"message": "User created successfully", "user_id": user_id}

@app.get("/preferences/{username}", response_model=User)
async def get_preferences(username: str) -> Optional[User]:
    conn = await get_db_connection()
    
    query = """
        SELECT 
            u.username, 
            u.course, 
            u.cafeteria, 
            u.city, 
            u.preferred_transport_medium,
            (SELECT STRING_AGG(s.stock_name, ',') 
            FROM user_stocks us
            JOIN stocks s ON us.s_id = s.s_id
            WHERE us.u_id = u.u_id) AS stocks,
            (SELECT STRING_AGG(n.news_name, ',') 
            FROM user_news un
            JOIN news n ON un.n_id = n.n_id
            WHERE un.u_id = u.u_id) AS news
        FROM users u
        WHERE u.username = $1;
    """

    result = await conn.fetchrow(query, username)
    await conn.close()
    
    if result:
        return User(
            username=result["username"],
            course=result["course"],
            cafeteria=result["cafeteria"],
            city=result["city"],
            preferred_transport_medium=result["preferred_transport_medium"],
            stocks=result["stocks"].split(",") if result["stocks"] else [],
            news=result["news"].split(",") if result["news"] else [],
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

#@app.put("/preferences/{username}")
#def update_preferences():
#    return {"Hello": "World"}