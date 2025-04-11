from enum import Enum

class Informations(Enum):
    NEWS_CATEGORY = (
        ("Business", "Entertainment", "General", "Health", "Science", "Sports", "Technology"),
        "News categories",
        "Some info",
        lambda x: x
    )

    TRAVEL_MEDIUM = (
        ("driving-car", "cycling-regular", "foot-walking", "wheelchair"),
        "Travel options",
        "Some info",
        lambda x: x
    )

    def __new__(cls, value, description, information_needed, func):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.information_needed = information_needed
        obj.func = func
        return obj