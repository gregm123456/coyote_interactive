# This file marks the screens directory as a package.

# Import all screen modules to make them accessible
from .network_screen import show_network_status
from .audio_screen import show_audio_devices
from .service_screen import show_service_management
from .transcript_screen import show_television_transcript
from .dialogue_screen import show_dialogue