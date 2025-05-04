from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Container
from services.audio import AudioManager
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from ui.widgets.audio_widgets import AudioDeviceWidget, MicrophoneWidget, OutputDeviceWidget

class AudioScreen(Widget):
    """Audio devices information and management screen."""
    
    # Add keyboard bindings
    BINDINGS = [
        # Number keys 0-9 for volume 0-90%
        Binding("0", "set_volume(0)", "Volume 0%"),
        Binding("1", "set_volume(1)", "Volume 10%"),
        Binding("2", "set_volume(2)", "Volume 20%"),
        Binding("3", "set_volume(3)", "Volume 30%"),
        Binding("4", "set_volume(4)", "Volume 40%"),
        Binding("5", "set_volume(5)", "Volume 50%"),
        Binding("6", "set_volume(6)", "Volume 60%"),
        Binding("7", "set_volume(7)", "Volume 70%"),
        Binding("8", "set_volume(8)", "Volume 80%"),
        Binding("9", "set_volume(9)", "Volume 90%"),
        # Key for 100%
        Binding("f", "set_volume(10)", "Full Volume (100%)"),
        # Keys for increment/decrement
        Binding("u", "increment_volume", "Volume Up"),
        Binding("d", "decrement_volume", "Volume Down"),
        # Refresh devices list
        Binding("r", "refresh", "Refresh Devices")
    ]
    
    # Track currently selected device
    selected_device = None
    
    def compose(self):
        """Compose the audio screen widgets."""
        yield Static("Audio Management", classes="title")
        
        self.audio_devices_container = Container(id="audio-devices")
        self.microphones_container = Container(id="microphones")
        
        yield Static("Audio Output Devices:")
        yield self.audio_devices_container
        
        yield Static("Microphones:")
        yield self.microphones_container
        
        yield Static("Keyboard Controls:", classes="section-header")
        yield Static("0-9: Set volume 0-90% | f: Full volume (100%) | u: Volume up | d: Volume down | r: Refresh devices")
        yield Static("Select a device first, then use keyboard controls to adjust volume")
        
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
            
        for device in devices:
            device_widget = OutputDeviceWidget(
                device_name=device["name"],
                volume=device["volume"],
                index=device["index"]
            )
            self.audio_devices_container.mount(device_widget)
            # Listen for selection events from this widget
            device_widget.on_message = self.handle_device_message

    def update_microphones(self):
        """Update the list of microphones."""
        mics = AudioManager.get_usb_microphones()
        self.microphones_container.remove_children()
        
        if not mics:
            self.microphones_container.mount(Static("No microphones found"))
            return
            
        for mic in mics:
            mic_widget = MicrophoneWidget(
                device_name=mic["name"],
                volume=mic["volume"],
                index=mic["index"]
            )
            self.microphones_container.mount(mic_widget)
            # Listen for selection events from this widget
            mic_widget.on_message = self.handle_device_message

    def handle_device_message(self, message):
        """Handle messages from device widgets."""
        if hasattr(message, "sender") and isinstance(message.sender, AudioDeviceWidget):
            if message.name == "device_selected":
                # When a device is selected, deselect all others
                self.deselect_all_devices_except(message.sender)
                self.selected_device = message.sender
        return True

    def deselect_all_devices_except(self, device):
        """Deselect all devices except the given one."""
        for child in self.audio_devices_container.children:
            if isinstance(child, AudioDeviceWidget) and child != device:
                child.selected = False
                child.refresh()
                
        for child in self.microphones_container.children:
            if isinstance(child, AudioDeviceWidget) and child != device:
                child.selected = False
                child.refresh()

    def on_button_pressed(self, event):
        """Handle button press events."""
        if event.button.id == "refresh":
            self.update_audio_devices()
            self.update_microphones()

    def action_set_volume(self, step: int):
        """Set volume for selected device to specified step."""
        if self.selected_device:
            is_sink = isinstance(self.selected_device, OutputDeviceWidget)
            self.selected_device.volume = AudioManager.set_volume_step(
                self.selected_device.index, 
                step, 
                is_sink
            )
            self.selected_device.refresh()

    def action_increment_volume(self):
        """Increase volume for selected device."""
        if self.selected_device:
            is_sink = isinstance(self.selected_device, OutputDeviceWidget)
            self.selected_device.volume = AudioManager.increment_volume(
                self.selected_device.index, 
                is_sink
            )
            self.selected_device.refresh()

    def action_decrement_volume(self):
        """Decrease volume for selected device."""
        if self.selected_device:
            is_sink = isinstance(self.selected_device, OutputDeviceWidget)
            self.selected_device.volume = AudioManager.decrement_volume(
                self.selected_device.index, 
                is_sink
            )
            self.selected_device.refresh()

    def action_refresh(self):
        """Refresh the device lists."""
        self.update_audio_devices()
        self.update_microphones()
