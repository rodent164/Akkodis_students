from akkodis_clients import client_gpt_4o
client_gpt, gpt_model = client_gpt_4o()
from chatmodule import Chat, client_gpt
import json

assistant = Chat("You are a helpful assistant that keep his messages short.", model=gpt_model)
user_input = input("Enter your message: ")
conversation_length = 0

tools = [
    {
        "type": "function",
        "function": {
            "name": "some_function",
            "description": "This function prints Hello world!",
            "parameters": {
                "type": "object",
                "properties": {
                    "number_of_rep": {
                        "type": "integer",
                        "description": "The number of times it should be printed."
                    },
                },
                "required": ["number_of_rep"]
            },
        }
    }
]

def some_function(number_of_rep):
    for ind in range (0,number_of_rep):
        print("Hello World!")

while conversation_length<5:
    assistant.add_user_message(user_input)

    # Call GPT with current chat + tool info
    response = client_gpt.chat.completions.create(
        model=gpt_model,
        messages = assistant.history,
        tools=tools,
        tool_choice="auto"
    )

    # If GPT called a tool...
    if response.choices[0].message.tool_calls is not None:
        tool_calls = response.choices[0].message.tool_calls
        assistant.add_tool_message(response.choices[0])  # Log tool call

        messages = []  # Store tool outputs
        for tool_call in tool_calls:
            # Get call ID and function name
            idcall = tool_call.id
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)  # Tool function arguments

            # Call actual function
            result = str(eval(function_name)(**args))
            messages.append({'role': 'tool', 'tool_call_id': idcall, 'content': result})
            #st.session_state.responses.append(result)
        assistant.add_tool_response_messages(messages)
    else:
        response = assistant.get_response(client_gpt)
        print("Assistant Response:", response)

    user_input = input("Enter your message: ")
    conversation_length = conversation_length + 1
