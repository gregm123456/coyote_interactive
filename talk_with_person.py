import config
import json
import os
from llm_chat_completion import llm_chat_completion
from speak_text import speak_text
from leds.led_manager import start_led, stop_led

# Global configuration variables
led_intercom = config.GPIO_LED_INTERCOM
transcript_file = config.TRANSCRIBE_LOG_FILE
person_prompt_start = config.PERSON_PROMPT_START
person_prompt_end = config.PERSON_PROMPT_END
person_prompt_no_transcript = config.PERSON_PROMPT_NO_TRANSCRIPT
conversation_file = os.path.join(config.CONVERSATION_DATA_PATH, config.CONVERSATION_FILE)
whisper_model = config.PERSON_WHISPER_MODEL
threads = config.PERSON_THREADS
conversation_file = os.path.join(config.CONVERSATION_DATA_PATH, config.CONVERSATION_FILE)
whisper_model = config.PERSON_WHISPER_MODEL
threads = config.PERSON_THREADS
mic = config.PERSON_MIC_NUMBER


def build_prompt_and_update_conversation(person_comment):
    # Use person prompt lines instead of television prompt lines
    # If person_comment contains any occurrences of "[ Silence ]" then remove them
    if "[ Silence ]" in person_comment:
        person_comment = person_comment.replace("[ Silence ]", "").strip()
    # if person_comment contains no a-z or A-Z, then set it to None
    if not any(char.isalpha() for char in person_comment):
        person_comment = None
    # Decide on the prompt content based on transcript availability
    if not person_comment:
        prompt = person_prompt_no_transcript
    else:
        prompt = person_prompt_start + person_comment + person_prompt_end

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
    with open(conversation_file, "w", encoding='utf-8') as f:  # Specify encoding
        json.dump(conversation, f, indent=4)

    return


def clean_response(response):
    sentence_endings = [".", "!", "?"]
    last_ending_index = max(response.rfind(ending) for ending in sentence_endings)
    if (last_ending_index != -1):
        response = response[:last_ending_index + 1]

    response = response.strip()
    response = response.replace("*", "")
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
        'whisper-stream',
        '-m', whisper_model,
        '--step', '4500',
        '--length', '5000',
        '-c', mic,
        '-t', threads,
        '-ac', '512',
        '--keep', '85',
        '-f', 'person_questions.txt'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    initial_duration = 5
    max_duration = 30
    time.sleep(initial_duration)
    if bm.get_initial_state():
        while recording and (time.time() - start_time < max_duration):
            time.sleep(0.1)
            if not bm.get_initial_state():
                time.sleep(1)
                break

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
    
    # Save the captured speech to a file in the conversation_data directory
    last_captured_speech_file = os.path.join(config.CONVERSATION_DATA_PATH, "last_captured_speech.txt")
    with open(last_captured_speech_file, "w", encoding='utf-8') as f:  # Specify encoding
        f.write(captured_speech)
        
    print("Captured speech:", captured_speech)
    return captured_speech


def talk_with_person(bm=None):

    led_thread = start_led(led_intercom, "constant")
    person_comment = capture_intercom_speech(bm)
    stop_led(led_thread)

    build_prompt_and_update_conversation(person_comment)

    # Start led_dynamite steady flashing during llm processing
    led_thread = start_led(led_intercom, "flashing")
    response = clean_response(llm_chat_completion(conversation_file))
    stop_led(led_thread)

    # FIRST append assistant response to conversation JSON file
    try:
        with open(conversation_file, "r", encoding='utf-8') as f:  # Specify encoding for reading too
            conversation = json.load(f)
    except Exception:
        conversation = []
    conversation.append({"role": "assistant", "content": response})
    with open(conversation_file, "w", encoding='utf-8') as f:  # Specify encoding
        json.dump(conversation, f, indent=4)
        
    # Save the cleaned response to last_coyote_reply.txt instead of last_coyote_response.txt
    reply_file = os.path.join(config.CONVERSATION_DATA_PATH, "last_coyote_reply.txt")
    with open(reply_file, "w", encoding='utf-8') as f:  # Specify encoding
        # Remove the JSON formatting (quotes) from the response for cleaner text
        clean_text = json.loads(response) if response.startswith('"') and response.endswith('"') else response
        f.write(clean_text)

    # THEN start led_intercom breathing pattern during speak_text
    led_thread = start_led(led_intercom, "breathing")
    speak_text(response)
    stop_led(led_thread)

    return



