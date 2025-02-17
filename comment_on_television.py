from config import TRANSCRIBE_LOG_FILE, RECENT_TRANSCRIPT_LINES
# Set local variables for the log file and transcript lines count
transcript_file = TRANSCRIBE_LOG_FILE
number_of_transcript_lines = RECENT_TRANSCRIPT_LINES

def comment_on_television():
    # Retrieve last number_of_transcript_lines from the transcript log file using the local variable
    with open(transcript_file, 'r') as f:
        lines = f.readlines()
    recent_transcript = " ".join(line.strip() for line in lines[-number_of_transcript_lines:])
    
    print("Commenting on television...")
    print("Recent transcript:", recent_transcript)
