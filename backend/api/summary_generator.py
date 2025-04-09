import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.usecase_handler import UseCaseHandler
from UseCases import UseCases
from api.data_filler import DataFiller

class UserSummaryGenerator:
    async def get_user_morning(self, user_id: str):
        use_cases = [UseCases.STOCKS.value, UseCases.NEWS.value, UseCases.WEATHER.value]
        api_data = await self.__get_api_data_without_gpt(use_cases, user_id)
        message = "Fass mir die wichtigsten Informationen für meinen Morgen zusammen. Geb mir das als einen zusammnhängenden Text zurück. Ohne Fomratierungen. Sag am Anfang Guten Morgen!"
        response = UseCaseHandler().get_response(message, api_data)
        return {"response": response}

    async def get_user_proactivity(self, user_id: str):
        use_cases = [UseCases.STOCKS.value, UseCases.NEWS.value]
        api_data = await self.__get_api_data_without_gpt(use_cases, user_id)
        stocks = api_data[UseCases.STOCKS.description]
        news = api_data[UseCases.NEWS.description]

        significant_stocks = self.__get_significant_stocks(stocks)
        recent_news = self.__get_recent_news(news)

        if not (significant_stocks or recent_news):
            return {"response": None}

        message = "Stell dir vor du bist proaktiv und erzählst mir etwas Neues über meine Aktien oder News. Erwähne bei den Aktien, wie sie sich in der letzten Stunde verändert haben. Beginne mit Hey, hast du schon gehört?"
        response = UseCaseHandler().get_response(message, api_data)
        return {"response": response}

    async def __get_api_data_without_gpt(self, use_cases, user_id: str):
        info_dict = {
            info: "" for use_case in UseCases if use_case.value in use_cases
            for info in use_case.information_needed
        }
        info = await DataFiller().fill_missing_values(info_dict, user_id)
        return UseCaseHandler().call_apis(use_cases, info)

    def __get_significant_stocks(self, stocks):
        return {stock_id: stock for stock_id, stock in stocks.items() if abs(float(stock.get("change1hour", 0))) > 1}

    def __get_recent_news(self, news):
        def within_last_hour(ts: str) -> bool:
            try:
                t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                return timedelta(0) <= (datetime.now(timezone.utc) - t) < timedelta(hours=1)
            except:
                return False
        return [a[0] for a in news.values() if a and within_last_hour(a[0].get("publishedAt", ""))]