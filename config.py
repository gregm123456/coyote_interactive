GPIO_BUTTON_INTERCOM = 27
GPIO_BUTTON_PLUNGER = 22
GPIO_SWITCH_LAMP = 17

BUTTON_LISTEN_TO_PERSON = GPIO_BUTTON_INTERCOM
BUTTON_LISTEN_TO_TELEVISION = GPIO_BUTTON_PLUNGER
SWITCH_WAKE_SLEEP = GPIO_SWITCH_LAMP

CONVERSATION_DATA_PATH = "conversation_data"

# Expected local development secrets are defined in config_secrets.py.
# To set up your local secrets, copy config_secrets.example.py to config_secrets.py and update the values.
try:
    from config_secrets import *
except ImportError:
    pass

TRANSCRIBE_LOG_FILE = "./audio_to_text/transcription.txt"
TRANSCRIBE_WHISPER_MODEL = "/usr/share/whisper/models/ggml-base.en.bin"

