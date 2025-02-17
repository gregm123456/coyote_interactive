# Module to comment on television content.
import os
import json
import time
import config
from llm_chat_completion import llm_chat_completion
from speak_text import speak_text
from leds.led_manager import start_led, stop_led  # new import

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
    # Start led_dynamite flashing steadily during prompt build
    led_thread = start_led(led_dynamite, "flashing")
    prompt = build_prompt_and_update_conversation()
    # wait
    time.sleep(5)
    stop_led(led_thread)
    
    # Start led_dynamite erratic flashing during llm processing
    led_thread = start_led(led_dynamite, "erratic")
    response = llm_chat_completion(conversation_file)
    stop_led(led_thread)
    
    # Start led_intercom breathing pattern during speak_text
    led_thread = start_led(led_intercom, "breathing")
    speak_text(response)
    stop_led(led_thread)
    
    return
