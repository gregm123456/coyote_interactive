from textual.app import App
from textual.widgets import Header, Footer
from textual.containers import Container
from ui.screens.network_screen import NetworkScreen
from ui.screens.audio_screen import AudioScreen
from ui.screens.service_screen import ServiceScreen

class MainApp(App):
    def compose(self):
        yield Header()
        yield Container(NetworkScreen(), AudioScreen(), ServiceScreen())
        yield Footer()

    def on_mount(self):
        self.set_title("Network and Audio Manager")

if __name__ == "__main__":
    MainApp.run()