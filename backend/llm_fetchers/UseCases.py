from llm import ChatGPTProcessor

chatGPTProcessor = ChatGPTProcessor()

def declare_usecase(user_input: str) -> str:
    prompt = (
        f"{user_input} "
        "You have 6 APIs: Stocks, News, Weather, Travel Time, Hotel Search, Flight Information. "
        "Please select all the APIs mentioned in the input and return a list of numbers corresponding exactly to the order of the APIs listed above."
        "Only give back a list of numbers."
    )
    return chatGPTProcessor.process_input(prompt)

# Query which information is required using the provided list of use cases

def get_information(user_input, information_needed) -> str:
    prompt = (
        f"Here is the information needed: {information_needed} and here is the prompt by the user: {user_input}. "
        "Is any information not provided by the user?"
        "Give back a list of information provided by the user."
        f"Base the list on the information needed: {information_needed} "
        "Only give back the lists in this format [information_needed: <value>,...] if there is no value just leave it empty"
        "If there is more than one value for one info return them like this [<value>,<value>]"
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

if __name__ == "__main__":
    user_input = "I want to know the weather in Stuttgart and I want to know the BBC and ARD news also tell me about my Stocks."
    use_case = declare_usecase(user_input)
    information_needed = "City, News Service, Stocks"
    information_got = get_information(user_input, information_needed)
    print(use_case)
    print(information_got)
