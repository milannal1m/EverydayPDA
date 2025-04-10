import unittest
from unittest.mock import patch, MagicMock
from services import get_stock_price, get_news, get_weather, get_meals_by_name_and_date, get_hotels

class TestServices(unittest.TestCase):
    @patch("services.requests.get")
    def test_get_stock_price_valid_symbol(self, mock_get):

        mock_get.side_effect = [

            MagicMock(status_code=200, json=lambda: {
                "values": [{"close": "150.23", "datetime": "2025-04-09 14:30:00"}]
            }),
            MagicMock(status_code=200, json=lambda: {"change": "0.5"})

        ]

        # Test the stock function with a valid symbol
        result = get_stock_price(["AAPL"])
        expected = {
            "AAPL": {
                "price": "150.23",
                "datetime": "2025-04-09 14:30:00",
                "changeFrom1hour": "0.5"
            }
        }

        self.assertEqual(result, expected)

    @patch("services.requests.get")
    def test_get_stock_price_invalid_symbol(self, mock_get):
        # Mock die API-Antwort für ein ungültiges Symbol
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"code": 400, "message": "Invalid symbol"})

        # Teste mit einem ungültigen Symbol
        result = get_stock_price(["INVALID"])
        expected = {}
        self.assertEqual(result, expected)

    @patch("services.requests.get")
    def test_get_news_valid_category(self, mock_get):

        # Mocks a succesful API response for a valid category

        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            "totalResults": 50,
            "articles": [
                {
                    "title": "Breaking News", 
                    "url": "http://example.com", 
                    "publishedAt": "2025-04-09T12:00:00Z"
                }
            ]
        })

        # Tests the news function with a valid category and defines a valid expected result

        result = get_news(["business"])
        expected = {
            "business": [
                {
                    "title": "Breaking News",
                    "source": "http://example.com",
                    "publishedAt": "2025-04-09T12:00:00Z"
                }
            ]
        }

        self.assertEqual(result, expected)

    @patch("services.requests.get")
    def test_get_news_invalid_category(self, mock_get):

        # Mocks a successful API response for an invalid response

        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            "totalResults": 0, 
            "articles": []
            })

        # Tests the news function with an invalid category and defines a expected result

        result = get_news(["Invalid"])
        expected = {}
        self.assertEqual(result, expected)

    @patch("services.requests.get")
    def test_get_weather_valid_city(self, mock_get):

        # Mocks a successful API response for a valid city

        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            "current": {
                "temp_c": "8.3",
                "feelslike_c": "6.5"
            },
            "forecast": {
                "forecastday": [
                    {
                        "day": {
                            "maxtemp_c": "10.5",
                            "mintemp_c": "5.0"
                        }
                    }
                ]
            }
        })

        # Tests the weather function with a valid city and defines a valid expected result

        result = get_weather(["Berlin"])
        expected = {
            "Berlin": {
                    "temperature": "8.3",
                    "feelslike": "6.5",
                    "max_temp": "10.5",
                    "min_temp": "5.0"	
            }
        }

        self.assertEqual(result, expected)

    @patch("services.requests.get")
    def test_get_weather_invalid_city(self, mock_get):

        # Mocks a successful API response for an invalid city

        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            "error": {
                "code": 1006,
                "message": "No matching location found."
            }
        })

        # Tests the weather function with an invalid city and defines a expected result

        result = get_weather(["Invalid"])
        expected = {}
        self.assertEqual(result, expected)

    @patch("services.requests.get")
    def test_get_hotels_valid_location_and_date(self, mock_get):

        # Mocks a successful API response for a valid location and date

        mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {
            "locationId": "11147",
            "location": {
                "name": "Berlin",
                "country": "Germany",
            },
            "hotelName": "Park Inn",
            "priceFrom": "231.78",
            "stars": "4"
        }
        ])

        # Tests the hotels function with a valid location and date

        result = get_hotels("Berlin", "2025-04-09", "2025-04-10")
        expected = {
            "Park Inn": {
                "price": "231.78",
                "stars": "4"
            }
        }

        self.assertEqual(result, expected)
    
    @patch("services.requests.get")
    def test_get_hotels_invalid_location_and_valid_date(self, mock_get):
        
        # Mocks a successful API response for an invalid location and valid date

        mock_get.return_value = MagicMock(status_code=200, json=lambda: [])

        # Tests the hotels function with an invalid location and valid date

        result = get_hotels("Invalid", "2025-04-09", "2025-04-10")
        expected = {}
        self.assertEqual(result, expected)

    @patch("services.requests.get")
    def test_get_hotels_valid_location_invalid_checkInDate(self, mock_get):

        # Mocks a successful API response for a valid location and invalid check-In date

        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            "status": "error",
            "errorCode": 2,
            "message": "checkIn: Must be formatted like yyyy-MM-dd"
        })

        # Tests the hotels function with a valid location and invalid check-In date

        result = get_hotels("Berlin", "25-04-09", "2025-04-10")
        expected = {}
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()