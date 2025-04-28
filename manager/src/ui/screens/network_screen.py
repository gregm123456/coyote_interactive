from textual.widget import Widget
from textual.widgets import Static, Button
from textual.containers import Container
from services.vpn import VPNManager
from services.wifi import WifiManager
from services.ethernet import EthernetService

class NetworkScreen(Widget):
    """Network information and management screen."""
    
    def compose(self):
        """Compose the network screen widgets."""
        yield Static("Network Status", classes="title")
        
        # VPN Section
        self.vpn_container = Container(id="vpn-section")
        yield Static("VPN Status:")
        yield self.vpn_container
        yield Button("Connect VPN", id="connect-vpn", variant="primary")
        yield Button("Disconnect VPN", id="disconnect-vpn", variant="error")
        
        # Ethernet Section
        self.ethernet_container = Container(id="ethernet-section")
        yield Static("Wired Network:")
        yield self.ethernet_container
        
        # WiFi Section
        self.wifi_container = Container(id="wifi-section")
        yield Static("Wireless Status:")
        yield self.wifi_container
        
        # Access Points
        self.ap_container = Container(id="access-points")
        yield Static("Available Access Points:")
        yield self.ap_container
        
        # Refresh Button
        yield Button("Refresh Network Info", id="refresh-network")

    def on_mount(self):
        """Initialize service managers and update UI when mounted."""
        # Initialize service classes
        self.vpn_manager = VPNManager()
        self.wifi_manager = WifiManager()
        self.ethernet_service = EthernetService()
        
        # Update UI with current information
        self.update_network_info()

    def update_network_info(self):
        """Update all network information sections."""
        self.update_vpn_status()
        self.update_wifi_status()
        self.update_ethernet_status()
        self.update_access_points()

    def update_vpn_status(self):
        """Update the VPN status display."""
        status = self.vpn_manager.get_vpn_status()
        self.vpn_container.remove_children()
        self.vpn_container.mount(Static(f"Status: {status}"))

    def update_wifi_status(self):
        """Update the WiFi status display."""
        status = self.wifi_manager.get_wifi_status()
        self.wifi_container.remove_children()
        self.wifi_container.mount(Static(f"Status: {status}"))

    def update_ethernet_status(self):
        """Update the Ethernet status display."""
        status = self.ethernet_service.get_status()
        info = self.ethernet_service.get_connection_info()
        
        self.ethernet_container.remove_children()
        for key, value in info.items():
            self.ethernet_container.mount(Static(f"{key}: {value}"))

    def update_access_points(self):
        """Update the list of available WiFi access points."""
        access_points = self.wifi_manager.get_access_points()
        
        self.ap_container.remove_children()
        if not access_points:
            self.ap_container.mount(Static("No access points available"))
            return
            
        for ap in access_points:
            if isinstance(ap, dict):
                if 'Error' in ap:
                    self.ap_container.mount(Static(f"Error: {ap['Error']}"))
                else:
                    ssid = ap.get('SSID', 'Unknown')
                    signal = ap.get('Signal', 'N/A')
                    security = ap.get('Security', 'N/A')
                    self.ap_container.mount(
                        Static(f"{ssid} (Signal: {signal}, Security: {security})")
                    )

    def on_button_pressed(self, event):
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "connect-vpn":
            result = self.vpn_manager.connect_vpn()
            self.update_vpn_status()
        
        elif button_id == "disconnect-vpn":
            result = self.vpn_manager.disconnect_vpn()
            self.update_vpn_status()
        
        elif button_id == "refresh-network":
            self.update_network_info()