from textual.widget import Widget
from textual.reactive import Reactive
from textual.containers import Container
from textual.widgets import Static, Button
from services.vpn import get_vpn_status
from services.wifi import get_wifi_status, get_access_points
from services.ethernet import get_ethernet_status
from services.audio import get_usb_microphones, get_audio_output_devices
from services.systemd import get_service_status, manage_service

class NetworkWidgets(Widget):
    vpn_status = Reactive("")
    wifi_status = Reactive("")
    ethernet_status = Reactive("")
    access_points = Reactive([])
    
    def on_mount(self):
        self.update_network_info()
        self.render_widgets()

    def update_network_info(self):
        self.vpn_status = get_vpn_status()
        self.wifi_status = get_wifi_status()
        self.ethernet_status = get_ethernet_status()
        self.access_points = get_access_points()

    def render_widgets(self):
        self.clear()
        self.add(Static(f"VPN Status: {self.vpn_status}"))
        self.add(Static(f"Wired Network Status: {self.ethernet_status}"))
        self.add(Static(f"Wireless Status: {self.wifi_status}"))
        
        access_point_widgets = Container()
        for ap in self.access_points:
            access_point_widgets.add(Static(f"Access Point: {ap['name']} - Status: {ap['status']}"))
        
        self.add(access_point_widgets)

        self.add(Button("Refresh", on_click=self.update_network_info))
        self.add(Button("Manage VPN", on_click=self.manage_vpn))

    def manage_vpn(self):
        # Logic to manage VPN connections
        pass

    def refresh(self):
        self.update_network_info()
        self.render_widgets()