import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.service_fetchers.canteen_service import get_canteen_info

class TestGetCanteen(unittest.TestCase):

    @patch('requests.get')
    def test_get_canteeen_success(self, mock_get):
        
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: [{
                    "id": "1202",
                    "name": "Stuttgart Mitte, Mensa Central",
                    "city": "Stuttgart"
                }]
            ),

            MagicMock(status_code = 200, json=lambda: [
                    {
                        "id": "2281754",
                        "name": "Flädlesuppe",
                        "category": "Vorspeise",
                        "prices": {
                            "students": "5.75",
                            "employees": "8.25"
                        }
                    }
                ]
            ),
            MagicMock(status_code=200, json=lambda: [])
        ]

        result = get_canteen_info(["Mensa Central"])
        expected = {
            "Mensa Central":
                {
                    "Flädlesuppe": {
                        "category": "Vorspeise",
                        "price": "5.75"
                    }
                }
        }


if __name__ == '__main__':
    unittest.main()