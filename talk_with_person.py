import config
import json
import os
from llm_chat_completion import llm_chat_completion
from speak_text import speak_text
from leds.led_manager import start_led, stop_led

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
    # This custom code will be written later.
    return

def clean_response(response):
    sentence_endings = [".", "!", "?"]
    last_ending_index = max(response.rfind(ending) for ending in sentence_endings)
    if (last_ending_index != -1):
        response = response[:last_ending_index + 1]

    response = response.strip()
    response = response.replace("*", "")
    response = response.replace("‘", "").replace("’", "").replace("'", "")
    response = response.replace('"', "")
    # Escape the string for JSON
    cleaned = json.dumps(response)
    return cleaned

def capture_intercom_speech(bm=None):
    import subprocess, time
    from buttons.button_manager import ButtonManager
    # Use the provided ButtonManager or instantiate a new one
    if bm is None:
        bm = ButtonManager(config.BUTTON_LISTEN_TO_PERSON)
        local_bm = True
    else:
        local_bm = False
    
    recording = True
    start_time = time.time()

    def on_press():
        nonlocal start_time
        start_time = time.time()

    def on_release():
        nonlocal recording
        recording = False

    bm.register_press_callback(on_press)
    bm.register_release_callback(on_release)

    command = [
        '/usr/local/bin/stream',
        '-m', '/home/robot/whisper.cpp/models/ggml-tiny.en.bin',
        '--step', '4000',
        '--length', '8000',
        '-c', '1',
        '-t', '1',
        '-ac', '512',
        '-f', 'person_questions.txt'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    initial_duration = 12
    max_duration = 30
    time.sleep(initial_duration)
    if bm.get_initial_state():
        while recording and (time.time() - start_time < max_duration):
            time.sleep(0.1)

    process.terminate()
    try:
        process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()

    bm.unregister_press_callback(on_press)
    bm.unregister_release_callback(on_release)

    # If bm was created locally, there's no extra cleanup needed.
    with open("person_questions.txt", "r") as f:
        captured_speech = f.read()
    
    return captured_speech

def talk_with_person(bm=None):
    
    led_thread = start_led(led_intercom, "constant")
    person_comment = capture_intercom_speech(bm)
    stop_led(led_thread)

    build_prompt_and_update_conversation(person_comment)

    # Start led_dynamite erratic flashing during llm processing
    led_thread = start_led(led_intercom, "flashing")
    response = clean_response(llm_chat_completion(conversation_file))
    stop_led(led_thread)
    
    # Start led_intercom breathing pattern during speak_text
    led_thread = start_led(led_intercom, "breathing")
    speak_text(response)
    
    # Append assistant response to conversation JSON file
    try:
        with open(conversation_file, "r") as f:
            conversation = json.load(f)
    except Exception:
        conversation = []
    conversation.append({"role": "assistant", "content": response})
    with open(conversation_file, "w") as f:
        json.dump(conversation, f, indent=4)
    
    stop_led(led_thread)
    
    return



