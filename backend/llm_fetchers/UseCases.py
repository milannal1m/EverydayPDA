from llm_fetchers.llm import ChatGPTProcessor

chatGPTProcessor = ChatGPTProcessor()

def declare_usecase(user_input: str) -> str:
    prompt = (
        f"{user_input} "
        "You have 6 APIs: Stocks, News, Weather, Travel Time, Hotel Search, Flight Information. "
        "Please select all the APIs mentioned in the input and return a list of numbers corresponding exactly to the order of the APIs listed above."
    )
    return chatGPTProcessor.process_input(prompt)

# Query which information is required using the provided list of use cases

def get_information(user_input, information_needed) -> str:
    prompt = (
        f"Here is the {information_needed} and here is the prompt by the user: {user_input}. "
        "Is any information not provided by the user?"
        "Give back a list of information that is not provided and one of the information provided by the user. "
        "Only give back the lists."
    )
    return chatGPTProcessor.process_input(prompt)

# Query using preferences to retrieve the missing information
# Merge the list of information provided by the prompt and preferences
# Execute the API calls to fetch the required information

def response(user_input, api_calls) -> str:
    prompt = (
        f"Here is the information provided by the API calls: {api_calls}. "
        f"And here is the prompt by the user: {user_input}. "
        "Please give back the response to the user."
    )
    return chatGPTProcessor.process_input(prompt)