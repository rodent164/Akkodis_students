# Import a function that returns a GPT client and model name
from akkodis_clients import client_gpt_4o
client_gpt, gpt_model = client_gpt_4o()  # Connect to Azure/OpenAI with proper keys

# Import the Chat class from your own module, which helps manage conversation history
from chatmodule import Chat, client_gpt
import json  # Used to parse arguments from JSON strings

# Create a new assistant with a system prompt and specify the model to use
assistant = Chat("You are a helpful assistant that keep his messages short.", model=gpt_model)

# Ask the user for an input message
user_input = input("Enter your message: ")

# Counter to limit how many turns the conversation can go on
conversation_length = 0

# Define a list of tools (functions) the assistant can use
tools = [
    {
        "type": "function",  # The tool is a function (not a code interpreter or retrieval)
        "function": {
            "name": "some_function",  # The name the assistant will use to call it
            "description": "This function prints Hello world!",  # What the function does
            "parameters": {  # Parameters the assistant must provide when calling the function
                "type": "object",  # The parameters are an object/dictionary
                "properties": {
                    "number_of_rep": {  # One parameter: number_of_rep
                        "type": "integer",  # Must be an integer
                        "description": "The number of times it should be printed."
                    },
                },
                "required": ["number_of_rep"]  # number_of_rep must be provided
            },
        }
    }
]

# Define the actual function that the assistant can call
def some_function(number_of_rep):
    for ind in range(number_of_rep):
        print("Hello World!")

# Main conversation loop - allows up to 5 back-and-forth turns
while conversation_length < 5:
    # Add the user's message to the chat history
    assistant.add_user_message(user_input)

    # Ask GPT for a response, allowing it to call tools if needed
    response = client_gpt.chat.completions.create(
        model=gpt_model,
        messages=assistant.history,  # Send the whole conversation so far
        tools=tools,  # Let GPT know what tools it can use
        tool_choice="auto"  # GPT can decide whether to call a tool or not
    )

    # Check if GPT decided to use a tool
    if response.choices[0].message.tool_calls is not None:
        tool_calls = response.choices[0].message.tool_calls  # Get the tool call info
        assistant.add_tool_message(response.choices[0])  # Log that GPT wanted to use a tool

        messages = []  # To store tool results for adding to chat history

        # Process each tool call GPT made
        for tool_call in tool_calls:
            idcall = tool_call.id  # Unique ID of the tool call
            function_name = tool_call.function.name  # The name of the function to call
            args = json.loads(tool_call.function.arguments)  # Convert GPT's string arguments to a dictionary

            # Call the actual Python function using its name and arguments
            result = str(eval(function_name)(**args))  # Call the function dynamically
            messages.append({
                'role': 'tool',
                'tool_call_id': idcall,
                'content': result  # Save the result so GPT can see it
            })

        # Add the tool outputs back to the chat so GPT can respond appropriately
        assistant.add_tool_response_messages(messages)

    else:
        # If GPT didn't use a tool, just print its assistant reply
        response = assistant.get_response(client_gpt)
        print("Assistant Response:", response)

    # Ask for a new user input for the next round
    user_input = input("Enter your message: ")
    conversation_length += 1  # Increase the conversation round counter
