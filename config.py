GPIO_BUTTON_INTERCOM = 27
GPIO_BUTTON_PLUNGER = 22
GPIO_SWITCH_LAMP = 17

BUTTON_LISTEN_TO_PERSON = GPIO_BUTTON_INTERCOM
BUTTON_LISTEN_TO_TELEVISION = GPIO_BUTTON_PLUNGER
SWITCH_WAKE_SLEEP = GPIO_SWITCH_LAMP

CONVERSATION_DATA_PATH = "conversation_data"

# Expected local development secrets are defined in config_local.py.
# To set up your local secrets, copy config_local.example.py to config_local.py and update the values.
try:
    from config_local import *
except ImportError:
    pass

