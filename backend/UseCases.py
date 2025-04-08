from enum import Enum
from service_fetchers.services import get_stock_price, get_news, get_weather, get_travel_time

def placeholder(*args, **kwargs):
    raise NotImplementedError("Diese Funktion ist noch nicht implementiert.")

class UseCases(Enum):
    STOCKS = (1, "Stock Market Information", ["Stocks"], get_stock_price)
    NEWS = (2, "Latest News Updates", ["News Services"], get_news)
    WEATHER = (3, "Weather Forecasts", ["City"], get_weather)
    CAFETERIA = (4, "Cafeteria Menu", ["Cafeteria Name"],placeholder)
    TIMETABLE = (5, "Class Timetable", ["Course Name"], placeholder)
    TRAVEL_TIME = (6, "Traveltime", ["Transport Medium", "Destination"], get_travel_time)
    HOTEL_SEARCH = (7, "Hotel Booking", ["Hotel_Destination", "Check-in Date", "Check-out Date"], placeholder)
    FLIGHT_INFORMATION = (8, "Flight Information", ["Flight_Destination", "Departure Date", "Return Date"], placeholder)


    def __new__(cls, value, description, information_needed, func):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, description, information_needed, func):
        self._value_ = value
        self.description = description
        self.information_needed = information_needed
        self.func = func