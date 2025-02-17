# Module to comment on television content.
import os
import json
import config
from llm_chat_completion import llm_chat_completion
from speak_text import speak_text

# Global configuration variables
led_dynamite = config.GPIO_LED_DYNAMITE
led_intercom = config.GPIO_LED_INTERCOM
transcript_file = config.TRANSCRIBE_LOG_FILE
number_of_transcript_lines = config.RECENT_TRANSCRIPT_LINES
television_prompt_start = config.TELEVISION_PROMPT_START
television_prompt_end = config.TELEVISION_PROMPT_END
television_prompt_no_transcript = config.TELEVISION_PROMPT_NO_TRANSCRIPT
conversation_file = os.path.join(config.CONVERSATION_DATA_PATH, config.CONVERSATION_FILE)

def build_prompt_and_update_conversation():

    # Attempt to read transcript file
    try:
        with open(transcript_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Build recent transcript string
    recent_transcript = " ".join(line.strip() for line in lines[-number_of_transcript_lines:] if line.strip())
    
    # Decide on the prompt content based on transcript availability
    if not recent_transcript:
        prompt = television_prompt_no_transcript
    else:
        prompt = television_prompt_start + recent_transcript + television_prompt_end
    
    # Display the prompt
    print("Prompt:", prompt)
    
    # Load existing conversation from JSON file
    try:
        with open(conversation_file, "r") as f:
            conversation = json.load(f)
    except Exception:
        conversation = []
    
    # Append new user message to the conversation
    conversation.append({"role": "user", "content": prompt})
    
    # Write updated conversation back to file
    with open(conversation_file, "w") as f:
        json.dump(conversation, f, indent=4)
    
    return

def comment_on_television():

    # Build prompt and update conversation history
    build_prompt_and_update_conversation()
    
    # Signal start of the TV comment process
    print("Commenting on television...")
    
    # Get response from the LLM using the updated conversation file
    response = llm_chat_completion(conversation_file)
    
    # Display and vocalize the response
    print("Response:", response)
    speak_text(response)
    
    return
