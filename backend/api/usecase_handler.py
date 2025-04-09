import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_fetchers.UseCaseProcessor import UseCaseProcessor
from UseCases import UseCases
from api.data_filler import DataFiller

class UseCaseHandler:
    async def get_use_cases_and_info(self, message: str, user_id: str):
        processor = UseCaseProcessor()
        use_cases = processor.declare_usecase(message)
        needed_info = ", ".join([
            info for use_case in UseCases if use_case.value in use_cases
            for info in use_case.information_needed
        ])
        info = processor.get_information(message, needed_info)
        info = await DataFiller().fill_missing_values(info, user_id)
        return use_cases, info

    def call_apis(self, use_cases, info):
        results = {}
        for uc_id in use_cases:
            use_case = UseCases(uc_id)
            missing = [key for key in use_case.information_needed if key not in info]
            if missing:
                raise KeyError(f"Missing keys {missing} for {use_case.name}")
            args = [info[key] for key in use_case.information_needed]
            results[use_case.description] = use_case.func(*args)
        return results

    def get_response(self, message, api_data):
        return UseCaseProcessor().response(message, api_data)