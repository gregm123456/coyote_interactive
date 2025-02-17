import config
from conversation_manager import conversation_setup
import threading
import subprocess
import time
import sys  # added import

def main_business(stop_event):
    """Run the main business operations until a stop signal is received."""
    print(f"Button to listen to person is set to: {config.BUTTON_LISTEN_TO_PERSON}")
    print(f"Button to listen to television is set to: {config.BUTTON_LISTEN_TO_TELEVISION}")
    print(f"Switch to wake/sleep is set to: {config.SWITCH_WAKE_SLEEP}")
    print(f"API Key for local development is set to: {config.API_KEY}")
    
    # Ensure the conversation directory is set up.
    conversation_directory = conversation_setup(config)
    print(f"Conversation directory ensured at: {conversation_directory}")
    
    # Loop until the stop event is triggered, checking every second.
    while not stop_event.is_set():
        print("Main business running...")
        if stop_event.wait(1):
            break
    print("Main business stopped.")

def start_transcriber():
    return subprocess.Popen([
        "python", "/home/robot/coyote_interactive/audio_to_text/transcribe_continuously.py",
        "--log_file_path", config.TRANSCRIBE_LOG_FILE,
        "--whisper_model", config.TRANSCRIBE_WHISPER_MODEL,
        "--threads", config.TRANSCRIBE_THREADS,
        "--mic", config.TRANSCRIBE_MIC_NUMBER
    ])

def main():
    """Start the transcriber process and main business thread, and manage graceful shutdown."""
    stop_event = threading.Event()
    business_thread = threading.Thread(target=main_business, args=(stop_event,))
    business_thread.daemon = True  # make the thread a daemon
    business_thread.start()
    
    max_restarts = 20
    restart_count = 0
    transcriber = start_transcriber()
    
    try:
        while business_thread.is_alive():
            retcode = transcriber.poll()
            if retcode is not None:
                restart_count += 1
                if restart_count > max_restarts:
                    stop_event.set()  # signal main_business to stop
                    business_thread.join(timeout=5)  # wait briefly for shutdown
                    sys.exit("Transcriber crashed too many times, stopping coyote.py")
                print(f"Transcriber ended with code {retcode}, restarting...")
                transcriber = start_transcriber()
            time.sleep(1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, shutting down...")
        stop_event.set()
        while business_thread.is_alive():
            business_thread.join(timeout=0.1)
    finally:
        transcriber.terminate()
        print("Transcriber process terminated.")
    
    print("Doing more stuff...")

if __name__ == "__main__":
    main()