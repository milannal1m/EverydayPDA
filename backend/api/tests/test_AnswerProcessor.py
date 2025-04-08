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

    @patch("AnswerProcessor.get_db_connection", new_callable=AsyncMock)
    @patch("AnswerProcessor.UseCaseProcessor")
    async def test_get_morning(self, mock_usecase_proc_class, mock_get_db):
        # Setup mock for UseCaseProcessor
        mock_proc = MagicMock()
        mock_proc.response.return_value = "Guten Morgen! Alles super."
        mock_usecase_proc_class.return_value = mock_proc

        # Mock DB values for Stocks, News, City
        mock_conn = AsyncMock()
        mock_conn.fetch.side_effect = [
            [("AAPL",)],          # Stocks
            [("Tagesschau",)],    # News
            [("Stuttgart",)]      # City
        ]
        mock_get_db.return_value = mock_conn

        # Run the actual function
        result = await self.processor.get_morning("milan")

        # Assertions
        self.assertIn("response", result)
        self.assertTrue(result["response"].startswith("Guten Morgen"))
        self.assertEqual(mock_conn.fetch.call_count, 3)
        mock_conn.fetch.assert_any_call(
            "SELECT stock_name FROM stocks s JOIN user_stocks us ON s.s_id = us.s_id JOIN users u ON us.u_id = u.u_id WHERE u.username = $1",
            "milan"
        )
        mock_conn.fetch.assert_any_call(
            "SELECT news_name FROM news n JOIN user_news un ON n.n_id = un.n_id JOIN users u ON un.u_id = u.u_id WHERE u.username = $1",
            "milan"
        )
        mock_conn.fetch.assert_any_call(
            "SELECT city FROM users WHERE username = $1",
            "milan"
        )


if __name__ == '__main__':
    unittest.main()
