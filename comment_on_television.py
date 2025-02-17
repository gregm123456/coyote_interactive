from config import TRANSCRIBE_LOG_FILE, RECENT_TRANSCRIPT_LINES, TELEVISION_PROMPT_START, TELEVISION_PROMPT_END, TELEVISION_PROMPT_NO_TRANSCRIPT
# Set local variables for the log file and transcript lines count
transcript_file = TRANSCRIBE_LOG_FILE
number_of_transcript_lines = RECENT_TRANSCRIPT_LINES
# Assign configuration prompts to local variables
television_prompt_start = TELEVISION_PROMPT_START
television_prompt_end = TELEVISION_PROMPT_END
television_prompt_no_transcript = TELEVISION_PROMPT_NO_TRANSCRIPT

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
    print("Commenting on television...")
