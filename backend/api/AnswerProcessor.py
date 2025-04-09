import sys
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_fetchers.UseCaseProcessor import UseCaseProcessor
import service_fetchers.services as services
from UseCases import UseCases
from api.database import get_db_connection
from service_fetchers.services import get_stock_price, get_news, get_weather

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
            'Transport Medium': "SELECT preferred_transport_medium FROM users WHERE username = $1",
            'Start_Airpot':  "SELECT city FROM users WHERE username = $1",
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
        return default_values.get(key, None)

    async def __fill_missing_values(self, data: Dict[str, str], user_id) -> Dict[str, str]:
        """
        Fill in missing values for required information.
        """
        for key in data.keys():
            if data[key] == [""] or data[key] == "":
                if key in ['Stocks', 'News Services', 'City', 'Cafeteria Name', 'Course Name', 'Transport Medium', 'Start_Airpot', 'Start_Location']:
                    data[key] = await self.__fetch_from_database(key, user_id) or None
                else:
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
        results = {}

        for use_case_id in use_cases:
            try:
                use_case = UseCases(use_case_id)
            except ValueError:
                raise ValueError(f"Invalid Use Case Identifier: {use_case_id}")

            missing_keys = [key for key in use_case.information_needed if key not in information_got]
            if missing_keys:
                raise KeyError(f"Missing keys {missing_keys} for Use Case: {use_case.name}")       

            args = [information_got[key] for key in use_case.information_needed]
            result = use_case.func(*args)
            results[use_case.description] = result

        return results
    
    async def __get_all_users(self):
        conn = await get_db_connection()
        try:
            user_ids = await conn.fetch("SELECT username FROM users")
            return user_ids
        finally:
            await conn.close()

    async def __get_api_data_without_gpt(self, use_cases, user_id):
        info_dict = {info: "" for use_case in UseCases if use_case.value in use_cases for info in use_case.information_needed}
        information_got = await self.__fill_missing_values(info_dict, user_id)
        api_data = self.__call_apis(use_cases, information_got)
        return api_data
    
    async def __get_user_morning(self,user_id):
        use_case_processor = UseCaseProcessor()
        use_cases = [UseCases.STOCKS.value, UseCases.NEWS.value, UseCases.WEATHER.value]
        api_data = await self.__get_api_data_without_gpt(use_cases, user_id)
        message = "Fass mir die wichtigsten Informationen für meinen Morgen zusammen. Geb mir das als einen zusammnhängenden Text zurück. Ohne Fomratierungen. Sag am Anfang Guten Morgen!"
        response = use_case_processor.response(message, api_data)
        return {"response": response}
    
    def __get_stocks_with_significant_change(self, stocks):
        """
        Returns stocks with significant changes (greater than 1€).
        """
        significant_stocks = []
        for symbol, data in stocks.items():
            change1hour = data.get("change1hour", 0)
            if change1hour:
                if abs(float(data.get("change1hour", 0))) > 1:
                    significant_stocks.append(data)
        return significant_stocks
    
    def __is_within_last_hour(self, timestamp_str: str) -> bool:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        timestamp = timestamp.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        time_diff = now - timestamp
        return timedelta(0) <= time_diff < timedelta(hours=1)

    def __get_newest_news(self, news):
        """
        Returns the most recent news articles.
        """
        newest_news = []
        for topic, article in news.items():
            if article:
                if self.__is_within_last_hour(article[0].get("publishedAt", "")):
                    newest_news.append(article[0])
        return newest_news

    async def __get_user_proactivity(self,user_id):
        use_case_processor = UseCaseProcessor()
        use_cases = [UseCases.STOCKS.value, UseCases.NEWS.value]
        api_data = await self.__get_api_data_without_gpt(use_cases, user_id)
        stocks = api_data[UseCases.STOCKS.description]
        news = api_data[UseCases.NEWS.description]
        significant_stocks = self.__get_stocks_with_significant_change(stocks)
        new_news = self.__get_newest_news(news)

        response = None
        message = None

        if significant_stocks or new_news:
            message = "Stell dir vor du bist proaktiv und erzählst mir etwas Neues über meine Aktien oder News. Erwähne bei den Aktien, wie sie sich in der letzten Stunde verändert haben. Beginne mit Hey, hast du schon gehört?"
            response = use_case_processor.response(message, api_data)

        return {"response": response}
    
    async def get_answer(self,message,user_id):
        use_case_processor = UseCaseProcessor()
        use_cases, information_got = await self.__get_use_cases_and_info(message,user_id)
        api_data = self.__call_apis(use_cases, information_got)
        response = use_case_processor.response(message, api_data)
        return {"response": response}
    
    async def get_morning(self) -> Dict[str, List[Dict[str, str]]]:
        user_ids = await self.__get_all_users()

        results = []
        for record in user_ids:
            user_id = record['username']
            try:
                morning_result = await self.__get_user_morning(user_id)
                results.append({
                    "user_id": str(user_id),
                    "response": morning_result.get("response", "Fehler beim Abrufen")
                })
            except Exception as e:
                results.append({
                    "user_id": str(user_id),
                    "response": f"Fehler: {str(e)}"
                })

        return {"results": results}
    
    async def get_proactivity(self) -> Dict[str, List[Dict[str, str]]]:
        user_ids = await self.__get_all_users()

        results = []
        for record in user_ids:
            user_id = record['username']
            try:
                proactivity_result = await self.__get_user_proactivity(user_id)
                results.append({
                    "user_id": str(user_id),
                    "response": proactivity_result.get("response", "Fehler beim Abrufen")
                })
            except Exception as e:
                results.append({
                    "user_id": str(user_id),
                    "response": f"Fehler: {str(e)}\nTraceback:\n{traceback.format_exc()}"
                })

        return {"results": results}