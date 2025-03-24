import unittest
from unittest.mock import patch
from llm import ChatGPTProcessor

class TestChatGPTProcessor(unittest.TestCase):

    def setUp(self):
        ChatGPTProcessor._instance = None

    def test_singleton_behavior(self):
        processor1 = ChatGPTProcessor()
        processor2 = ChatGPTProcessor()
        self.assertIs(processor1, processor2, "Both instances should be identical")

    @patch("llm.openai.ChatCompletion.create")
    def test_process_input_success(self, mock_create):
        # Simulate a successful response from OpenAI
        mock_create.return_value = {
            "choices": [{
                "message": {"content": "Test response"}
            }]
        }
        processor = ChatGPTProcessor()
        result = processor.process_input("Test message")
        self.assertEqual(result, "Test response")
        mock_create.assert_called_once()

    @patch("llm.openai.ChatCompletion.create")
    def test_process_input_error(self, mock_create):
        # Simulate an API error
        mock_create.side_effect = Exception("API error")
        processor = ChatGPTProcessor()
        with self.assertRaises(Exception) as context:
            processor.process_input("Test message")
        self.assertIn("Error processing input", str(context.exception))

if __name__ == "__main__":
    unittest.main()