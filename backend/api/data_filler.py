from typing import Dict, Optional
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.database import get_db_connection

class DataFiller:
    @staticmethod
    async def __fetch_from_database(key: str, user_id: str) -> Optional[str]:
        query_map = {
            'Stocks': "SELECT stock_name FROM stocks s JOIN user_stocks us ON s.s_id = us.s_id JOIN users u ON us.u_id = u.u_id WHERE u.username = $1",
            'News Services': "SELECT news_name FROM news n JOIN user_news un ON n.n_id = un.n_id JOIN users u ON un.u_id = u.u_id WHERE u.username = $1",
            'City': "SELECT city FROM users WHERE username = $1",
            'Cafeteria Name': "SELECT cafeteria FROM users WHERE username = $1",
            'Course Name': "SELECT course FROM users WHERE username = $1",
            'Transport Medium': "SELECT preferred_transport_medium FROM users WHERE username = $1",
            'Start_Airpot': "SELECT city FROM users WHERE username = $1",
            'Start_Location': "SELECT city FROM users WHERE username = $1",
        }

        query = query_map.get(key)
        if not query:
            return None

        conn = await get_db_connection()
        try:
            result = await conn.fetch(query, user_id)
            return [record[0] for record in result] if result else None
        finally:
            await conn.close()

    @staticmethod
    def __get_default_value(key: str) -> str:
        default_values = {
            'Destination': 'DHBW Stuttgart',
            'Hotel_Destination': 'Maldives',
            'Flight_Destination': 'Maldives',
            'Check-in Date': '2025-05-05',
            'Check-out Date': '2025-05-27',
            'Departure Date': '2025-05-05',
            'Return Date': '2025-05-27'
        }
        return default_values.get(key)

    async def fill_missing_values(self, data: Dict[str, str], user_id: str) -> Dict[str, str]:
        for key in data:
            if data[key] == "" or data[key] == [""]:
                if key in ['Stocks', 'News Services', 'City', 'Cafeteria Name', 'Course Name', 'Transport Medium', 'Start_Airpot', 'Start_Location']:
                    data[key] = await self.__fetch_from_database(key, user_id) or None
                else:
                    data[key] = self.__get_default_value(key)
        return data