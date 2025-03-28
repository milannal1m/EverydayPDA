from llm import ChatGPTProcessor

class UseCaseProcessor(ChatGPTProcessor):
    def __init__(self):
        super().__init__()
    
    def declare_usecase(self, user_input: str) -> str:
        prompt = (
            f"{user_input} "
            "You have 6 APIs: Stocks, News, Weather, Travel Time, Hotel Search, Flight Information. "
            "Please select all the APIs mentioned in the input and return a list of numbers corresponding exactly to the order of the APIs listed above."
            "Only give back a list of numbers."
        )
        return self.process_input(prompt)
    
    # Query which information is required using the provided list of use cases
    
    def get_information(self, user_input: str, information_needed: str) -> str:
        prompt = (
            f"Here is the information needed: {information_needed} and here is the prompt by the user: {user_input}. "
            "Is any information not provided by the user? "
            "Give back a list of information provided by the user. "
            f"Base the list on the information needed: {information_needed} "
            "Only give back the lists in this format [information_needed: <value>,...] if there is no value just leave it empty. "
            "If there is more than one value for one info return them like this [<value>,<value>]"
        )
        return self.process_input(prompt)
    
    # Query using preferences to retrieve the missing information
    # Merge the list of information provided by the prompt and preferences
    # Execute the API calls to fetch the required information

    def response(self, user_input: str, api_calls: str) -> str:
        prompt = (
            f"Here is the information provided by the API calls: {api_calls}. "
            f"And here is the prompt by the user: {user_input}. "
            "Please give back the response to the user."
        )
        return self.process_input(prompt)

if __name__ == "__main__":
    user_input = "I want to know the weather in Stuttgart and I want to know the BBC and ARD news also tell me about my Stocks."
    information_needed = "City, News Service, Stocks"
    
    processor = UseCaseProcessor()
    use_case = processor.declare_usecase(user_input)
    information_got = processor.get_information(user_input, information_needed)
    
    print(use_case)
    print(information_got)
