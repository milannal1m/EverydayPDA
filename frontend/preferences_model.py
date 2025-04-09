class UserPreferences:
    def __init__(self, user_id, course="", cafeteria="", city="", transport="", stocks=None, news=None):
        self.user_id = user_id
        self.course = course
        self.cafeteria = cafeteria
        self.city = city
        self.transport = transport
        self.stocks = stocks if stocks else []
        self.news = news if news else []

    def to_json(self):
        return {
            "username": str(self.user_id),
            "course": self.course,
            "cafeteria": self.cafeteria,
            "city": self.city,
            "preferred_transport_medium": self.transport,
            "stocks": self.stocks,
            "news": self.news
        }