import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Type
from openai import OpenAI

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
        client = OpenAI() 
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}],
                max_tokens=400
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception("Error processing input: " + str(e))

    def process_input_with_context(self, user_input: str, context: str, schema: Type[BaseModel]) -> BaseModel:
        client = OpenAI() 
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_input}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema.__name__,
                        "schema": schema.model_json_schema()
                    }
                }
            )
            parsed_response = response.choices[0].message.parsed
            if not parsed_response:
                # Fallback: manually parse the output using the schema
                parsed_response = schema.model_validate_json(response.choices[0].message.content)
            return parsed_response
        except Exception as e:
            raise Exception("Error processing structured input: " + str(e))

#Example:
#if __name__ == "__main__":
#    processor1 = ChatGPTProcessor()
#    processor2 = ChatGPTProcessor()
#    print(processor1 is processor2)   # This should print True to confirm the singleton behavior.
#    user_input = "Hello, how is the weather today in Stuttgart?"
#    response = processor1.process_input(user_input)
#    print(response)