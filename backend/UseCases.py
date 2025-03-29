from enum import Enum

class UseCases(Enum):
    STOCKS = (1, "Stock Market Information", ["Stocks"])
    NEWS = (2, "Latest News Updates", ["News Services"])
    WEATHER = (3, "Weather Forecasts", ["City"])
    CAFETERIA = (4, "Cafeteria Menu", ["Cafeteria Name"])
    TIMETABLE = (5, "Class Timetable", ["Course Name"])
    TRAVEL_TIME = (6, "Traveltime", ["Transport Medium", "Destination"])
    HOTEL_SEARCH = (7, "Hotel Booking", ["Hotel_Destination", "Check-in Date", "Check-out Date"])
    FLIGHT_INFORMATION = (8, "Flight Information", ["Flight_Destination", "Departure Date", "Return Date"])

    def __init__(self, value, description, information_needed):
        self._value_ = value
        self.description = description
        self.information_needed = information_needed