from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Container
from services.audio import AudioManager
from textual.reactive import reactive

class AudioScreen(Widget):
    """Audio devices information and management screen."""
    
    def compose(self):
        """Compose the audio screen widgets."""
        yield Static("Audio Management", classes="title")
        
        self.audio_devices_container = Container(id="audio-devices")
        self.microphones_container = Container(id="microphones")
        
        yield Static("Audio Output Devices:")
        yield self.audio_devices_container
        
        yield Static("Microphones:")
        yield self.microphones_container
        
        yield Button("Refresh", id="refresh", variant="primary")

    def on_mount(self):
        """Initialize and update audio devices when mounted."""
        self.update_audio_devices()
        self.update_microphones()

    def update_audio_devices(self):
        """Update the list of audio output devices."""
        devices = AudioManager.get_audio_output_devices()
        self.audio_devices_container.remove_children()
        
        if not devices:
            self.audio_devices_container.mount(Static("No audio devices found"))
            return
            
        for idx, device in enumerate(devices):
            # Now handling dictionary format instead of AudioDevice objects
            device_widget = Static(f"{device['index']}: {device['name']} (Volume: {device['volume']}%)")
            self.audio_devices_container.mount(device_widget)

    def update_microphones(self):
        """Update the list of microphones."""
        mics = AudioManager.get_usb_microphones()
        self.microphones_container.remove_children()
        
        if not mics:
            self.microphones_container.mount(Static("No microphones found"))
            return
            
        for idx, mic in enumerate(mics):
            # Now handling dictionary format instead of AudioDevice objects
            mic_widget = Static(f"{mic['index']}: {mic['name']} (Volume: {mic['volume']}%)")
            self.microphones_container.mount(mic_widget)

    def on_button_pressed(self, event):
        """Handle button press events."""
        if event.button.id == "refresh":
            self.update_audio_devices()
            self.update_microphones()

    # Method for selecting audio devices/microphones can be added here if needed