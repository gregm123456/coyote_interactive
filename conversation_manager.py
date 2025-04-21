__all__ = ['conversation_setup']

import os
import json


def conversation_setup(config):
    # new local variables from config
    conversation_directory = config.CONVERSATION_DATA_PATH
    system_message_text = config.SYSTEM_MESSAGE_TEXT
    conversation_file_name = config.CONVERSATION_FILE  # new local variable for conversation file name

    if not os.path.exists(conversation_directory):
        os.makedirs(conversation_directory)

    # Use the local variable for the conversation file name.
    conversation_file = os.path.join(conversation_directory, conversation_file_name)
    if not os.path.exists(conversation_file):
        # starter conversation with system entry
        starter_conversation = [
            {
                "role": "system",
                "content": system_message_text
            }
        ]
        with open(conversation_file, "w") as json_file:
            json.dump(starter_conversation, json_file, indent=4)

    return conversation_directory
