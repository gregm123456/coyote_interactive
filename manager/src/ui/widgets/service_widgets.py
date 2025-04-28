from textual import events
from textual.widget import Widget
from textual.containers import Container
from textual.widgets import Button, Static, Label
from services.systemd import manage_service_status

class ServiceWidget(Widget):
    def __init__(self):
        super().__init__()
        self.service_status = Static("Service Status: Unknown")
        self.start_button = Button(label="Start Service", on_click=self.start_service)
        self.stop_button = Button(label="Stop Service", on_click=self.stop_service)

    def render(self):
        return Container(
            self.service_status,
            self.start_button,
            self.stop_button,
        )

    async def on_mount(self):
        await self.update_service_status()

    async def update_service_status(self):
        status = await manage_service_status("coyote.service")
        self.service_status.update(f"Service Status: {status}")

    async def start_service(self):
        await manage_service_status("coyote.service", action="start")
        await self.update_service_status()

    async def stop_service(self):
        await manage_service_status("coyote.service", action="stop")
        await self.update_service_status()