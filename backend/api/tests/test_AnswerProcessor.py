import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from answer_processor import AnswerProcessor, UseCases


class TestAnswerProcessor(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.processor = AnswerProcessor()

    @patch("answer_processor.get_db_connection", new_callable=AsyncMock)
    @patch("answer_processor.UseCaseProcessor")
    async def test_get_answer(self, mock_usecase_proc_class, mock_get_db):
        # Setup mock for UseCaseProcessor
        mock_proc = MagicMock()
        mock_proc.declare_usecase.return_value = [UseCases.STOCKS]
        mock_proc.get_information.return_value = {"Stocks": ""}
        mock_proc.response.return_value = "Apple steht gut."
        mock_usecase_proc_class.return_value = mock_proc

        # Mock DB result for missing stock
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [("AAPL",)]  # Simulating DB response for stock
        mock_get_db.return_value = mock_conn

        # Run the actual function
        result = await self.processor.get_answer("Wie steht Apple?", "milan")

        # Assertions
        self.assertIn("response", result)
        self.assertEqual(result["response"], "Apple steht gut.")
        mock_proc.response.assert_called_once()
        mock_conn.fetch.assert_called_once_with(
            "SELECT stock_name FROM stocks s JOIN user_stocks us ON s.s_id = us.s_id JOIN users u ON us.u_id = u.u_id WHERE u.username = $1",
            "milan"
        )

    @patch('answer_processor.get_db_connection')  # Mock der Datenbankverbindung
    async def test_get_morning(self, mock_get_db_connection):
        # Mock der Rückgabe der fetch Methode der Datenbankverbindung (Benutzer abfragen)
        mock_db_connection = AsyncMock()
        mock_db_connection.fetch.return_value = [
            {"username": "user1"},
            {"username": "user2"}
        ]
        mock_get_db_connection.return_value = mock_db_connection

        # Mock der Rückgabe von __fetch_from_database (Datenbankabfragen simulieren)
        with patch.object(AnswerProcessor, '_AnswerProcessor__fetch_from_database', new_callable=AsyncMock) as mock_fetch_from_db:
            mock_fetch_from_db.side_effect = lambda key, user_id: {
                'Stocks': ['AAPL'],
                'News Services': ['Tech News'],
                'City': ['Stuttgart'],
                'Cafeteria Name': ['Campus Cafeteria'],
                'Course Name': ['Computer Science'],
                'Transport Medium': ['Bus']
            }.get(key, None)

            # Erstelle den AnswerProcessor
            answer_processor = AnswerProcessor()

            # Führe get_morning aus
            result = await answer_processor.get_morning()

            for user_result in result['results']:
                # Überprüfe, ob die user_id richtig ist
                self.assertIn('user_id', user_result)
                self.assertIn(user_result['user_id'], ['user1', 'user2'])
                self.assertTrue(user_result['response'].startswith("Guten Morgen"))

    @patch('answer_processor.get_db_connection')  # Mock der Datenbankverbindung
    async def test_get_morning_with_no_users(self, mock_get_db_connection):
        # Mock der Rückgabe der fetch Methode der Datenbankverbindung (Keine Benutzer)
        mock_db_connection = AsyncMock()
        mock_db_connection.fetch.return_value = []  # Keine Benutzer in der DB
        mock_get_db_connection.return_value = mock_db_connection

        # Erstelle den AnswerProcessor
        answer_processor = AnswerProcessor()

        # Führe get_morning aus
        result = await answer_processor.get_morning()

        # Überprüfe, ob das Ergebnis leer ist
        expected_result = {"results": []}
        self.assertEqual(result, expected_result)

    @patch.object(AnswerProcessor, '_AnswerProcessor__get_all_users', new_callable=AsyncMock)
    @patch.object(AnswerProcessor, '_AnswerProcessor__get_api_data_without_gpt', new_callable=AsyncMock)
    async def test_get_proactivity_with_real_logic(self, mock_get_api_data, mock_get_all_users):
        # Arrange
        mock_get_all_users.return_value = [{'username': 'user1'}]

        timestamp = (datetime.now(timezone.utc) - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        mock_get_api_data.return_value = {
            'Stock Market Information': {'AAL': {'price': '9.080000', 'datetime': '2025-04-08 15:59:00', 'change1hour': '1.1'}, 'AAPL': {'price': '172.77000', 'datetime': '2025-04-08 15:59:00', 'change1hour': '-0.11999512'}}
            , 'Latest News Updates': {'Technology': [{'title': 'Google Releases Android Update to Patch Two Actively Exploited Vulnerabilities - The Hacker News', 'source': 'https://thehackernews.com/2025/04/google-releases-android-update-to-patch.html', 'publishedAt': f"{timestamp}"}]}
            }

        # Act
        result = await self.processor.get_proactivity()

        # Assert
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["user_id"], "user1")
        self.assertIn("Hey, hast du schon gehört", result["results"][0]["response"])

    @patch.object(AnswerProcessor, '_AnswerProcessor__get_all_users', new_callable=AsyncMock)
    @patch.object(AnswerProcessor, '_AnswerProcessor__get_api_data_without_gpt', new_callable=AsyncMock)
    async def test_get_proactivity_no_changes(self, mock_get_api_data, mock_get_all_users):
        # Arrange
        mock_get_all_users.return_value = [{'username': 'user1'}]

        timestamp = (datetime.now(timezone.utc) - timedelta(minutes=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        mock_get_api_data.return_value = {
            'Stock Market Information': {'AAL': {'price': '9.080000', 'datetime': '2025-04-08 15:59:00', 'change1hour': '0.0012998581'}, 'AAPL': {'price': '172.77000', 'datetime': '2025-04-08 15:59:00', 'change1hour': '-0.11999512'}}
            , 'Latest News Updates': {'Technology': [{'title': 'Google Releases Android Update to Patch Two Actively Exploited Vulnerabilities - The Hacker News', 'source': 'https://thehackernews.com/2025/04/google-releases-android-update-to-patch.html', 'publishedAt': f"{timestamp}"}]}
            }

        # Act
        result = await self.processor.get_proactivity()

        # Assert
        self.assertIsNone(result["results"][0]["response"])  # keine Antwort ohne Veränderung

    @patch.object(AnswerProcessor, '_AnswerProcessor__get_all_users', new_callable=AsyncMock)
    @patch.object(AnswerProcessor, '_AnswerProcessor__get_api_data_without_gpt', new_callable=AsyncMock)
    async def test_get_proactivity_error_handling(self, mock_get_api_data, mock_get_all_users):
        # Arrange
        mock_get_all_users.return_value = [{'username': 'user1'}]
        
        mock_get_api_data.side_effect = Exception("API failed")

        # Act
        result = await self.processor.get_proactivity()

        # Assert
        self.assertIn("Error: API failed", result["results"][0]["response"])


if __name__ == '__main__':
    unittest.main()
