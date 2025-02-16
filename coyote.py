import config
from conversation_manager import conversation_setup
import threading
import subprocess

def main():
    print(f"Button to listen to person is set to: {config.BUTTON_LISTEN_TO_PERSON}")
    print(f"Button to listen to television is set to: {config.BUTTON_LISTEN_TO_TELEVISION}")
    print(f"Switch to wake/sleep is set to: {config.SWITCH_WAKE_SLEEP}")
    print(f"API Key for local development is set to: {config.API_KEY}")
    
    # Call conversation_setup to ensure the conversation directory exists.
    conversation_directory = conversation_setup(config)
    print(f"Conversation directory ensured at: {conversation_directory}")
    
    try:
        transcriber = subprocess.Popen([
            "python", "/home/robot/coyote_interactive/audio_to_text/transcribe_continuously.py",
            "--log_file_path", config.TRANSCRIBE_LOG_FILE,
            "--whisper_model", config.TRANSCRIBE_WHISPER_MODEL
        ])
        # add a temporary line here to just keep the script running and not exit
        input("Press Enter to exit...")
    finally:
        transcriber.terminate()
        # Optionally, wait for the process to terminate:
        # transcriber.wait()

if __name__ == "__main__":
    main()
