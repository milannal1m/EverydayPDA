from enum import Enum
from service_fetchers.services import get_stock_price, get_news, get_weather, get_canteen_info, get_rapla_schedule, get_travel_info, get_hotels, get_flights

#def placeholder(*args, **kwargs):
    #raise NotImplementedError("Diese Funktion ist noch nicht implementiert.")

class UseCases(Enum):
    STOCKS = (1, "Stock Market Information", ["Stock-Name"], get_stock_price)
    NEWS = (2, "Latest News Updates", ["News-Topic"], get_news)
    WEATHER = (3, "Weather Forecasts", ["City"], get_weather)
    CAFETERIA = (4, "Canteen Menu", ["Canteen-Name"], get_canteen_info)
    TIMETABLE = (5, "Rapla-Class-Schedule", ["Date"], get_rapla_schedule)
    TRAVEL_TIME = (6, "Traveltime", ["Transport-Medium", "Start-Location" "Destination-Location"], get_travel_info)
    HOTEL_SEARCH = (7, "Hotel Booking", ["Hotel-Destination", "Check-in-Date", "Check-out-Date"], get_hotels)
    FLIGHT_INFORMATION = (8, "Flight Information", ["Start-Airport", "Destination-Airport", "Departure-Date", "Return-Date"], get_flights)


    def __new__(cls, value, description, information_needed, func):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, description, information_needed, func):
        self._value_ = value
        self.description = description
        self.information_needed = information_needed
        self.func = func