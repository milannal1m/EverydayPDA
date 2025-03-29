from pydantic import BaseModel
from typing import Dict, List, Optional

class User(BaseModel):
    username: str
    course: str
    cafeteria: str
    city: str
    preferred_transport_medium: str
    stocks: Optional[List[str]] = []
    news: Optional[List[str]] = []

class UserUpdate(BaseModel):
    course: Optional[str] = None
    cafeteria: Optional[str] = None
    city: Optional[str] = None
    preferred_transport_medium: Optional[str] = None
    add_stocks: Optional[List[str]] = []
    delete_stocks: Optional[List[str]] = []
    add_news: Optional[List[str]] = []
    delete_news: Optional[List[str]] = []

