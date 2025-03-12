import openai
import os
from dotenv import load_dotenv

class ChatGPTProcessor:
    def __init__(self):
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        env_path = os.path.join(BASE_DIR, ".env")
        load_dotenv(env_path)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found. Please set in .env file.")
        openai.api_key = api_key

    def process_input(self, user_input: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}],
                max_tokens=70
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception("Error processing input: " + str(e))

#Example:
#if __name__ == "__main__":
#    processor = ChatGPTProcessor()
#    user_input = "Hello, how is the weather today in Stuttgart?"
#    response = processor.process_input(user_input)
#    print(response)