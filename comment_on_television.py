import os
import json
import config
from llm_chat_completion import llm_chat_completion
from speak_text import speak_text

# Consolidated config assignments
transcript_file = config.TRANSCRIBE_LOG_FILE
number_of_transcript_lines = config.RECENT_TRANSCRIPT_LINES
television_prompt_start = config.TELEVISION_PROMPT_START
television_prompt_end = config.TELEVISION_PROMPT_END
television_prompt_no_transcript = config.TELEVISION_PROMPT_NO_TRANSCRIPT
conversation_file = os.path.join(config.CONVERSATION_DATA_PATH, config.CONVERSATION_FILE)

def comment_on_television():

    # Retrieve last number_of_transcript_lines from the transcript log file using the local variable
    try:
        with open(transcript_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    
    # Check if file has no lines or only whitespace
    recent_transcript = " ".join(line.strip() for line in lines[-number_of_transcript_lines:] if line.strip())
    if not recent_transcript:
        prompt = television_prompt_no_transcript
    else:
        prompt = television_prompt_start + recent_transcript + television_prompt_end
    
    print("Prompt:", prompt)
    
    # Removed local assignment for conversation_file; using the global variable instead.
    try:
        with open(conversation_file, "r") as f:
            conversation = json.load(f)
    except Exception:
        conversation = []
    conversation.append({"role": "user", "content": prompt})
    with open(conversation_file, "w") as f:
        json.dump(conversation, f, indent=4)
    
    print("Commenting on television...")

    response = llm_chat_completion()
    print("Response:", response)

    speak_text(response)
    
    return
