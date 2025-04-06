import openai
import os
from dotenv import load_dotenv

class ChatGPTProcessor:
    _instance = None 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatGPTProcessor, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent reinitialization of the singleton
        if hasattr(self, "_initialized") and self._initialized:
            return
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        env_path = os.path.join(BASE_DIR, ".env")
        load_dotenv(env_path)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found. Please set in .env file.")
        openai.api_key = api_key
        self._initialized = True

    def process_input(self, user_input: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}],
                max_tokens=400
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception("Error processing input: " + str(e))

#Example:
#if __name__ == "__main__":
#    processor1 = ChatGPTProcessor()
#    processor2 = ChatGPTProcessor()
#    print(processor1 is processor2)   # This should print True to confirm the singleton behavior.
#    user_input = "Hello, how is the weather today in Stuttgart?"
#    response = processor1.process_input(user_input)
#    print(response)