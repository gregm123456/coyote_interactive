import config
from conversation_manager import conversation_setup, archive_conversation
from buttons.button_manager import ButtonManager
import threading
import subprocess
import time
import sys


def coyote_alive(stop_event):
    """Run the coyote alive operations until a stop signal is received."""
    button_listen_to_person = config.BUTTON_LISTEN_TO_PERSON
    button_listen_to_television = config.BUTTON_LISTEN_TO_TELEVISION
    switch_wake_sleep = config.SWITCH_WAKE_SLEEP

    # Instantiate ButtonManagers for each GPIO pin.
    bm_person = ButtonManager(button_listen_to_person)
    bm_television = ButtonManager(button_listen_to_television)
    bm_wake_sleep = ButtonManager(switch_wake_sleep)

    # Loop until the stop event is triggered, checking every second.
    while not stop_event.is_set():
        if bm_wake_sleep.get_initial_state():
            # Wake mode logic
            if bm_television.get_initial_state():
                # Ensure conversation directory exists before TV interaction
                conversation_setup(config)
                import comment_on_television
                comment_on_television.comment_on_television()
            if bm_person.get_initial_state():
                # Ensure conversation directory exists before person interaction
                conversation_setup(config)
                import talk_with_person
                talk_with_person.talk_with_person(bm_person)
        else:
            # Sleep mode logic - check for both buttons pressed simultaneously
            if bm_television.get_initial_state() and bm_person.get_initial_state():
                # Archive the current conversation before BOOM
                archived_file = archive_conversation(config)
                if archived_file:
                    print(f"Conversation archived to: {archived_file}")
                print("BOOM!")
        if stop_event.wait(0.1):
            break
    print("Coyote alive operations stopped.")


def start_transcriber():
    return subprocess.Popen([
        "python", "/home/robot/coyote_interactive/audio_to_text/transcribe_continuously.py",
        "--log_file_path", config.TRANSCRIBE_LOG_FILE,
        "--whisper_model", config.TRANSCRIBE_WHISPER_MODEL,
        "--threads", config.TRANSCRIBE_THREADS,
        "--mic", config.TRANSCRIBE_MIC_NUMBER
    ])


def main():
    """Start the transcriber process and coyote alive thread, and manage graceful shutdown."""
    stop_event = threading.Event()
    business_thread = threading.Thread(target=coyote_alive, args=(stop_event,))
    business_thread.daemon = True
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
                    stop_event.set()
                    business_thread.join(timeout=5)
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
