import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app, User

class TestGetPreferences(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)  

    @patch("main.get_db_connection")  
    async def test_get_preferences(self, mock_get_db_connection):
        
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetchrow.return_value = {
            "username": "testuser",
            "course": "Computer Science",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Bike",
            "stocks": "Apple,Google",
            "news": "CNN,BBC"
        }

        response = self.client.get("/preferences/testuser")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "username": "testuser",
            "course": "Computer Science",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Bike",
            "stocks": ["Apple", "Google"],
            "news": ["CNN", "BBC"]
        })

    @patch("main.get_db_connection")
    async def test_get_preferences_user_not_found(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.fetchrow.return_value = None 

        response = self.client.get("/preferences/nonexistentuser")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})

class TestInitPreferences(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("main.get_db_connection")
    async def test_init_preferences_success(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn

        mock_transaction = AsyncMock()
        mock_conn.transaction.return_value = mock_transaction
        mock_transaction.__aenter__.return_value = mock_conn

        mock_conn.fetchval.side_effect = [0,100,None,200,201,None,300,301]
        mock_conn.fetchrow.return_value = None

        user_data = {
            "username": "testuser",
            "course": "Computer Science",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Bike",
            "stocks": ["Apple", "Google"],
            "news": ["CNN", "BBC"]
        }

        response = self.client.post("/preferences/init", json=user_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User created successfully", "user_id": 100})

        mock_conn.fetchval.assert_any_call("SELECT COUNT(*) FROM users WHERE username = $1", "testuser")

    @patch("main.get_db_connection")
    async def test_init_preferences_user_already_exists(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn

        mock_conn.fetchval.side_effect = [1]

        user_data = {
            "username": "existinguser",
            "course": "Math",
            "cafeteria": "Main Hall",
            "city": "Berlin",
            "preferred_transport_medium": "Car",
            "stocks": ["Tesla"],
            "news": ["Reuters"]
        }

        response = self.client.post("/preferences/init", json=user_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "User already exists"})

    @patch("main.get_db_connection")
    async def test_init_preferences_with_existing_stocks_and_news(self, mock_get_db_connection):
        mock_conn = AsyncMock()
        mock_get_db_connection.return_value = mock_conn

        mock_conn.fetchval.side_effect = [0, 43, 10, 11, 20, 21]

        user_data = {
            "username": "testuser2",
            "course": "Physics",
            "cafeteria": "Science Cafe",
            "city": "Hamburg",
            "preferred_transport_medium": "Train",
            "stocks": ["Amazon", "Microsoft"],
            "news": ["NYT", "Guardian"]
        }

        response = self.client.post("/preferences/init", json=user_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User created successfully", "user_id": 43})

        mock_conn.fetchval.assert_any_call("SELECT s_id FROM stocks WHERE stock_name = $1", "Amazon")
        mock_conn.fetchval.assert_any_call("SELECT s_id FROM stocks WHERE stock_name = $1", "Microsoft")
        mock_conn.fetchval.assert_any_call("SELECT n_id FROM news WHERE news_name = $1", "NYT")
        mock_conn.fetchval.assert_any_call("SELECT n_id FROM news WHERE news_name = $1", "Guardian")

if __name__ == "__main__":
    unittest.main()
