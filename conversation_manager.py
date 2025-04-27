__all__ = ['conversation_setup', 'archive_conversation']

import os
import json
import datetime


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


def archive_conversation(config):
    """
    Archives the current conversation file by renaming it with a timestamp.
    """
    conversation_directory = config.CONVERSATION_DATA_PATH
    conversation_file_name = config.CONVERSATION_FILE
    
    # Full path to the current conversation file
    conversation_file = os.path.join(conversation_directory, conversation_file_name)
    
    # Check if the conversation file exists before attempting to archive
    if os.path.exists(conversation_file):
        # Generate timestamp down to the second (YYYYMMDD_HHMMSS format)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create the new filename with timestamp
        base_name = os.path.splitext(conversation_file_name)[0]  # Remove .json extension
        extension = os.path.splitext(conversation_file_name)[1]  # Get .json extension
        archived_file_name = f"{base_name}_{timestamp}{extension}"
        
        # Full path to the archived file
        archived_file = os.path.join(conversation_directory, archived_file_name)
        
        # Rename the file
        os.rename(conversation_file, archived_file)
        return archived_file
    return None
