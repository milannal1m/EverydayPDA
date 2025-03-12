from fastapi import FastAPI, Query, HTTPException
import asyncpg
from typing import Dict, List, Optional
from pydantic import BaseModel 
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_fetchers.llm import ChatGPTProcessor


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

DATABASE_URL = "postgresql://user:password@preferences_db:5432/preferences_db"

async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

chatGPTProcessor = ChatGPTProcessor()

@app.get("/answer")
def get_answer(message: str = Query(..., min_length=1)):
    answer = chatGPTProcessor.process_input(message)
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
    async with conn.transaction():
        check_query = "SELECT COUNT(*) FROM users WHERE username = $1"
        existing = await conn.fetchval(check_query, user.username)

        if existing > 0:
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

from pydantic import BaseModel
from typing import List, Optional

class UserUpdate(BaseModel):
    course: Optional[str] = None
    cafeteria: Optional[str] = None
    city: Optional[str] = None
    preferred_transport_medium: Optional[str] = None
    add_stocks: Optional[List[str]] = []
    delete_stocks: Optional[List[str]] = []
    add_news: Optional[List[str]] = []
    delete_news: Optional[List[str]] = []

async def __update_list_preferences(conn, user_id, items, table, id_column, name_column, link_table, link_column):
    """Fügt Elemente hinzu oder entfernt sie basierend auf den gegebenen Listen."""
    add_items = items.get("add", [])
    delete_items = items.get("delete", [])
    
    if add_items:
        for item_name in add_items:
            item_id = await conn.fetchval(f"SELECT {id_column} FROM {table} WHERE {name_column} = $1", item_name)
            if not item_id:
                item_id = await conn.fetchval(f"INSERT INTO {table} ({name_column}) VALUES ($1) RETURNING {id_column}", item_name)
            await conn.execute(f"INSERT INTO {link_table} (u_id, {link_column}) VALUES ($1, $2) ON CONFLICT DO NOTHING", user_id, item_id)
    
    if delete_items:
        for item_name in delete_items:
            await conn.execute(f"DELETE FROM {link_table} WHERE u_id = $1 AND {link_column} = (SELECT {id_column} FROM {table} WHERE {name_column} = $2)", user_id, item_name)

@app.put("/preferences/{username}")
async def update_preferences(username: str, user: UserUpdate):
    conn = await get_db_connection()
    async with conn.transaction():
        check_query = "SELECT u_id FROM users WHERE username = $1"
        user_id = await conn.fetchval(check_query, username)
        
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_fields = []
        update_values = []
        
        if user.course:
            update_fields.append("course = $1")
            update_values.append(user.course)
        if user.cafeteria:
            update_fields.append("cafeteria = $2")
            update_values.append(user.cafeteria)
        if user.city:
            update_fields.append("city = $3")
            update_values.append(user.city)
        if user.preferred_transport_medium:
            update_fields.append("preferred_transport_medium = $4")
            update_values.append(user.preferred_transport_medium)
        
        if update_fields:
            update_query = f"""
                UPDATE users
                SET {', '.join(update_fields)}
                WHERE u_id = $5
            """
            await conn.execute(update_query, *update_values, user_id)
        
        # Aktien aktualisieren
        await __update_list_preferences(conn, user_id, {"add": user.add_stocks, "delete": user.delete_stocks}, "stocks", "s_id", "stock_name", "user_stocks", "s_id")
        
        # News aktualisieren
        await __update_list_preferences(conn, user_id, {"add": user.add_news, "delete": user.delete_news}, "news", "n_id", "news_name", "user_news", "n_id")
        
    await conn.close()
    return {"message": "User preferences updated successfully"}
