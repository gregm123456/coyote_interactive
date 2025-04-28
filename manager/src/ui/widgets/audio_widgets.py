from textual.widget import Widget
from textual.reactive import Reactive
from textual.containers import Container
from textual.widgets import Static, Slider, Button

class AudioDeviceWidget(Widget):
    device_name = Reactive("")
    volume = Reactive(0)
    index = Reactive(0)

    def __init__(self, device_name: str, volume: int, index: int):
        super().__init__()
        self.device_name = device_name
        self.volume = volume
        self.index = index

    def render(self) -> Container:
        return Container(
            Static(f"Device: {self.device_name} (ID: {self.index})"),
            Slider(value=self.volume, min=0, max=100, step=1, label="Volume"),
            Button(label="Select", on_click=self.select_device)
        )

    def select_device(self):
        # Logic to select the audio device
        pass


class MicrophoneWidget(AudioDeviceWidget):
    def render(self) -> Container:
        return Container(
            Static(f"Microphone: {self.device_name} (ID: {self.index})"),
            Slider(value=self.volume, min=0, max=100, step=1, label="Volume"),
            Button(label="Select", on_click=self.select_device)
        )


class OutputDeviceWidget(AudioDeviceWidget):
    def render(self) -> Container:
        return Container(
            Static(f"Output Device: {self.device_name} (ID: {self.index})"),
            Slider(value=self.volume, min=0, max=100, step=1, label="Volume"),
            Button(label="Select", on_click=self.select_device)
        )