__all__ = ['conversation_setup']

import os

def conversation_setup(config):

    conversation_directory = config.CONVERSATION_DATA_PATH

    if not os.path.exists(conversation_directory):
        os.makedirs(conversation_directory)
    return conversation_directory
