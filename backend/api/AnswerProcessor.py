import sys
import os
from typing import Dict, List, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_fetchers.UseCaseProcessor import UseCaseProcessor
import service_fetchers.services as services
from UseCases import UseCases
from api.database import get_db_connection

class AnswerProcessor:
    _instance = None 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AnswerProcessor, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent reinitialization of the singleton
        if hasattr(self, "_initialized") and self._initialized:
            return
        
    async def __fetch_from_database(self, key: str, user_id: str) -> Optional[str]:
        """
        Holt fehlende Werte aus der PostgreSQL-Datenbank basierend auf dem Benutzernamen.
        """
        query_map = {
            'Stocks': "SELECT stock_name FROM stocks s JOIN user_stocks us ON s.s_id = us.s_id JOIN users u ON us.u_id = u.u_id WHERE u.username = $1",
            'News Services': "SELECT news_name FROM news n JOIN user_news un ON n.n_id = un.n_id JOIN users u ON un.u_id = u.u_id WHERE u.username = $1",
            'City': "SELECT city FROM users WHERE username = $1",
            'Cafeteria Name': "SELECT cafeteria FROM users WHERE username = $1",
            'Course Name': "SELECT course FROM users WHERE username = $1",
            'Transport Medium': "SELECT preferred_transport_medium FROM users WHERE username = $1"
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


    def __get_default_value(self,key: str) -> str:
        """
        Standard values for information not provided by the user.
        """
        default_values = {
            'Destination': 'DHBW Stuttgart',
            'Hotel_Destination': 'Maldives',
            'Flight_Destination': 'Maldives',
            'Check-in Date': '2025-05-05',
            'Check-out Date': '2025-05-27',
            'Departure Date': '2025-05-05',
            'Return Date': '2025-05-27'
        }
        return default_values.get(key, 'Unknown')

    async def __fill_missing_values(self, data: Dict[str, str], user_id) -> Dict[str, str]:
        """
        Fill in missing values for required information.
        """
        for key in data.keys():
            if data[key] == "":
                if key in ['Stocks', 'News Services', 'City', 'Cafeteria Name', 'Course Name', 'Transport Medium']:
                    data[key] = await self.__fetch_from_database(key, user_id) or 'Unknown'
                    None
                else:
                    print(key)
                    data[key] = self.__get_default_value(key)
        return data
    
    async def __get_use_cases_and_info(self,message,user_id):
        use_case_processor = UseCaseProcessor()
        use_cases = use_case_processor.declare_usecase(message)
        information_needed = ", ".join([info for use_case in UseCases if use_case.value in use_cases for info in use_case.information_needed])
        information_got = use_case_processor.get_information(message, information_needed)
        information_got = await self.__fill_missing_values(information_got, user_id)
        return use_cases, information_got
    
    def __call_apis(self, use_cases, information_got):
        None

    async def get_answer(self,message,user_id):
        use_case_processor = UseCaseProcessor()
        use_cases, information_got = await self.__get_use_cases_and_info(message,user_id)
        #api_data = self.__call_apis(use_cases, information_got)
        #response = use_case_processor.response(message, api_data)
        #return {"response": response}
        return {"use_cases": use_cases, "information_needed": information_got}

        
    