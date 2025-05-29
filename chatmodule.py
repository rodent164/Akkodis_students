from AI_Tutorial.akkodis_clients import client_gpt_4o
from openai.types.chat import (ChatCompletionToolMessageParam,
                               ChatCompletionSystemMessageParam,
                               ChatCompletionUserMessageParam,
                               ChatCompletionAssistantMessageParam,
                               )

client_gpt, gpt_model = client_gpt_4o()

import logging
import os

# Set up logging
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(SCRIPT_DIR, "chat_history.log")
logging.basicConfig(
    filename=log_file_path,
    filemode="w",  # <-- This overwrites the file each time
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


class Chat:
    def __init__(self, system_prompt, model): #model="gpt-4o")
        self.model = model
        self.history = [
            {"role": "system", "content": system_prompt}
        ]
        self.log_chat_history()

    def add_user_message(self, message):
        self.history.append({"role": "user", "content": message})
        self.log_chat_history()

    def get_response(self, client):
        completion = client.chat.completions.create(
            model=self.model,
            messages=self.history
        )
        response = completion.choices[0].message.content
        self.history.append({"role": "assistant", "content": response})
        self.log_chat_history()
        return response

    def add_tool_message(self, tool_calls):
        assistant_msg = ChatCompletionAssistantMessageParam(
            role='assistant',
            content=tool_calls.message.content,
            tool_calls=tool_calls.message.tool_calls
        )
        self.history.append(assistant_msg)
        self.log_chat_history()

    def add_tool_response_messages(self, messages):  # accepts a list of tool messages
        for mes in messages:
            self.history.append(ChatCompletionToolMessageParam(
                role="tool",
                tool_call_id=mes["tool_call_id"],
                content=mes["content"]
            ))
        self.log_chat_history(len(messages))

    def log_chat_history(self, last_n: int = 1):
        if last_n == 1:
            messages = [self.history[-1]]
        else:
            messages = self.history[-last_n:]

        logging.info("🔁 Chat History Update:")
        for msg in messages:
            logging.info(str(msg))
        logging.info("-" * 60)
