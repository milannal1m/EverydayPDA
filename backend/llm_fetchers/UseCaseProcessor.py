import ast
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UseCases import UseCases
from llm_fetchers.ChatGPTProcessor import ChatGPTProcessor

from pydantic import BaseModel
from typing import List, Dict

class UseCaseSelection(BaseModel):
    use_case_ids: List[int]

class ExtractedInformation(BaseModel):
    info: Dict[str, List[str]]

class UseCaseProcessor(ChatGPTProcessor):
    def __init__(self):
        super().__init__()

    def parse_response(self, response: str):
        try:
            return ast.literal_eval(response)
        except Exception:
            return response
    
    def declare_usecase(self, user_input: str) -> List[int]:
        use_cases = ", ".join(f"{use_case.value}: {use_case.description}" for use_case in UseCases)
        context = (
            f"You are given this user input: {user_input} "
            "If the input isn't in English, internally translate it. "
            f"Available APIs with their IDs are listed here: {use_cases}. "
            "Return a list of numbers corresponding to the APIs mentioned in the user input."
        )
        structured = self.process_input_with_context(user_input, context, UseCaseSelection)
        valid_ids = [uc.value for uc in UseCases]
        selected_ids = self.parse_response(structured.use_case_ids)
        return [uid for uid in selected_ids if uid in valid_ids]

    def get_information(self, user_input: str, information_needed: str) -> dict:
        context = (
            f"These are the required fields: {information_needed}. "
            f"Here's the user input: {user_input}. "
            "If the input isn't in English, internally translate it. "
            "Return a dictionary where each key is one of the fields, and the value is a list of strings provided in the input."
            "Usually the information provided is a single word"
            "If the value isn't provided always return ['']. Never return the whole question. Only return the dictionary."  
        )
        structured = self.process_input_with_context(user_input, context, ExtractedInformation)
        return self.parse_response(structured.info)
    
    # Query using preferences to retrieve the missing information
    # Merge the list of information provided by the prompt and preferences
    # Execute the API calls to fetch the required information

    def response(self, user_input: str, api_calls: str) -> str:
        prompt = (
            f"Here is the information provided by the API calls: {api_calls}. "
            f"And here is the prompt by the user: {user_input}. "
            "Ensure the response is provided in plain text and in the same language as the user input."
        )
        return self.process_input(prompt)

if __name__ == "__main__":
    user_input = "Wie lange habe ich heute Uni und wie steht es heute um den Kurs von Microsoft?"
    information_needed = "Stocks, News Services, City, Cafeteria Name, Course Name, Transport Medium, Destination, Check-in Date, Check-out Date, Departure Date, Return Date"

    processor = UseCaseProcessor()
    use_case = processor.declare_usecase(user_input)
    info = processor.get_information(user_input, information_needed)

    print(use_case)  # e.g., [1, 5]
    print(info)      # e.g., {'Stocks': [''], 'News Services': [''], 'City': [''], 'Cafeteria Name': [''], 'Course Name': [''], 'Transport Medium': [''], 'Destination': [''], 'Check-in Date': [''], 'Check-out Date': [''], 'Departure Date': [''], 'Return Date': ['']}