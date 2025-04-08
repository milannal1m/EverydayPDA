import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AnswerProcessor import AnswerProcessor, UseCases


class TestAnswerProcessor(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.processor = AnswerProcessor()

    @patch("AnswerProcessor.get_db_connection", new_callable=AsyncMock)
    @patch("AnswerProcessor.UseCaseProcessor")
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

    @patch("AnswerProcessor.get_db_connection")
    @patch.object(AnswerProcessor, "_AnswerProcessor__get_user_morning", new_callable=AsyncMock)
    async def test_get_morning_success(self, mock_get_user_morning, mock_get_db_connection):
        # Mocked database result
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [{'username': 'user1'}, {'username': 'user2'}]
        mock_get_db_connection.return_value = mock_conn

        # Mocked user morning response
        mock_get_user_morning.side_effect = [
            {"response": "Guten Morgen! Es wird heute sonnig."},
            {"response": "Guten Morgen! Der Aktienmarkt sieht vielversprechend aus."}
        ]

        processor = AnswerProcessor()
        result = await processor.get_morning()

        expected = {
            "results": [
                {"user_id": "user1", "response": "Guten Morgen! Es wird heute sonnig."},
                {"user_id": "user2", "response": "Guten Morgen! Der Aktienmarkt sieht vielversprechend aus."}
            ]
        }

        self.assertEqual(result, expected)
        mock_get_user_morning.assert_any_call("user1")
        mock_get_user_morning.assert_any_call("user2")
        self.assertEqual(mock_get_user_morning.call_count, 2)
        mock_conn.fetch.assert_called_once_with("SELECT username FROM users")
        mock_conn.close.assert_awaited_once()

    @patch("AnswerProcessor.get_db_connection")
    @patch.object(AnswerProcessor, "_AnswerProcessor__get_user_morning", new_callable=AsyncMock)
    async def test_get_morning_with_error(self, mock_get_user_morning, mock_get_db_connection):
        # Mocked DB result
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [{'username': 'user1'}, {'username': 'user2'}]
        mock_get_db_connection.return_value = mock_conn

        # First user succeeds, second fails
        mock_get_user_morning.side_effect = [
            {"response": "Guten Morgen! Wetter ist super."},
            Exception("Fehler beim Abrufen der Daten")
        ]

        processor = AnswerProcessor()
        result = await processor.get_morning()

        expected = {
            "results": [
                {"user_id": "user1", "response": "Guten Morgen! Wetter ist super."},
                {"user_id": "user2", "response": "Fehler: Fehler beim Abrufen der Daten"}
            ]
        }

        self.assertEqual(result, expected)
        self.assertEqual(mock_get_user_morning.call_count, 2)
        mock_conn.close.assert_awaited_once()

if __name__ == '__main__':
    unittest.main()
