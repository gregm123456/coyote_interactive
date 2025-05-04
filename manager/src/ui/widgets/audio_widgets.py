from textual.widget import Widget
from textual.reactive import Reactive
from textual.containers import Container, Horizontal
from textual.widgets import Static, Slider, Button
from services.audio import AudioManager

class AudioDeviceWidget(Widget):
    device_name = Reactive("")
    volume = Reactive(0)
    index = Reactive(0)
    selected = Reactive(False)

    def __init__(self, device_name: str, volume: int, index: int):
        super().__init__()
        self.device_name = device_name
        self.volume = volume
        self.index = index

    def render(self) -> Container:
        # Create volume buttons for 0%, 50%, 100% 
        vol_buttons = Horizontal(
            Button("0%", id=f"vol_{self.index}_0", classes="vol-btn"),
            Button("50%", id=f"vol_{self.index}_5", classes="vol-btn"),
            Button("100%", id=f"vol_{self.index}_10", classes="vol-btn"),
            Button("↓", id=f"vol_{self.index}_down", classes="vol-btn"),
            Button("↑", id=f"vol_{self.index}_up", classes="vol-btn"),
            id="volume-controls"
        )
        
        # Selection indicator
        selection_indicator = " [SELECTED]" if self.selected else ""
        
        return Container(
            Static(f"Device: {self.device_name} (ID: {self.index}){selection_indicator}"),
            Static(f"Volume: {self.volume}%"),
            vol_buttons,
            Button(label="Select", id=f"select_{self.index}")
        )

    def on_button_pressed(self, event):
        button_id = event.button.id
        
        # Handle volume control buttons
        if button_id and button_id.startswith(f"vol_{self.index}_"):
            parts = button_id.split("_")
            if len(parts) == 3:
                # Handle specific volume levels
                if parts[2] in ["0", "5", "10"]:
                    step = int(parts[2])
                    is_sink = isinstance(self, OutputDeviceWidget)
                    self.volume = AudioManager.set_volume_step(self.index, step, is_sink)
                    self.refresh()
                # Handle up/down volume controls
                elif parts[2] == "up":
                    is_sink = isinstance(self, OutputDeviceWidget)
                    self.volume = AudioManager.increment_volume(self.index, is_sink)
                    self.refresh()
                elif parts[2] == "down":
                    is_sink = isinstance(self, OutputDeviceWidget)
                    self.volume = AudioManager.decrement_volume(self.index, is_sink)
                    self.refresh()
        
        # Handle device selection button
        elif button_id and button_id == f"select_{self.index}":
            self.selected = True
            self.refresh()
            # Emit a custom message that the parent can catch to deselect other devices
            self.emit_no_wait("device_selected", self)


class MicrophoneWidget(AudioDeviceWidget):
    def render(self) -> Container:
        # Create volume buttons for 0%, 50%, 100% 
        vol_buttons = Horizontal(
            Button("0%", id=f"vol_{self.index}_0", classes="vol-btn"),
            Button("50%", id=f"vol_{self.index}_5", classes="vol-btn"),
            Button("100%", id=f"vol_{self.index}_10", classes="vol-btn"),
            Button("↓", id=f"vol_{self.index}_down", classes="vol-btn"),
            Button("↑", id=f"vol_{self.index}_up", classes="vol-btn"),
            id="volume-controls"
        )
        
        # Selection indicator
        selection_indicator = " [SELECTED]" if self.selected else ""
        
        return Container(
            Static(f"Microphone: {self.device_name} (ID: {self.index}){selection_indicator}"),
            Static(f"Volume: {self.volume}%"),
            vol_buttons,
            Button(label="Select", id=f"select_{self.index}")
        )


class OutputDeviceWidget(AudioDeviceWidget):
    def render(self) -> Container:
        # Create volume buttons for 0%, 50%, 100% 
        vol_buttons = Horizontal(
            Button("0%", id=f"vol_{self.index}_0", classes="vol-btn"),
            Button("50%", id=f"vol_{self.index}_5", classes="vol-btn"),
            Button("100%", id=f"vol_{self.index}_10", classes="vol-btn"),
            Button("↓", id=f"vol_{self.index}_down", classes="vol-btn"),
            Button("↑", id=f"vol_{self.index}_up", classes="vol-btn"),
            id="volume-controls"
        )
        
        # Selection indicator
        selection_indicator = " [SELECTED]" if self.selected else ""
        
        return Container(
            Static(f"Output Device: {self.device_name} (ID: {self.index}){selection_indicator}"),
            Static(f"Volume: {self.volume}%"),
            vol_buttons,
            Button(label="Select", id=f"select_{self.index}")
        )