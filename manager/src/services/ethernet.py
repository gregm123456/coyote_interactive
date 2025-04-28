from typing import List, Dict
import subprocess

class EthernetService:
    def __init__(self):
        self.interface = self.get_active_interface()
        self.status = self.get_status()

    def get_active_interface(self) -> str:
        """Get the name of the active Ethernet interface."""
        try:
            result = subprocess.run(['ip', 'link', 'show', 'up'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'state UP' in line:
                    return line.split(':')[1].strip()
        except Exception as e:
            print(f"Error getting active interface: {e}")
        return ""

    def get_status(self) -> str:
        """Get the status of the Ethernet connection."""
        if self.interface:
            return "Connected"
        return "Disconnected"

    def get_ip_address(self) -> str:
        """Get the IP address of the active Ethernet interface."""
        try:
            result = subprocess.run(['ip', 'addr', 'show', self.interface], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'inet ' in line:
                    return line.split()[1]
        except Exception as e:
            print(f"Error getting IP address: {e}")
        return "N/A"

    def get_mac_address(self) -> str:
        """Get the MAC address of the active Ethernet interface."""
        try:
            result = subprocess.run(['cat', f'/sys/class/net/{self.interface}/address'], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"Error getting MAC address: {e}")
        return "N/A"

    def restart_connection(self) -> None:
        """Restart the Ethernet connection."""
        try:
            subprocess.run(['sudo', 'systemctl', 'restart', 'networking'], check=True)
        except Exception as e:
            print(f"Error restarting connection: {e}")

    def get_connection_info(self) -> Dict[str, str]:
        """Get detailed connection information."""
        return {
            "Interface": self.interface,
            "Status": self.status,
            "IP Address": self.get_ip_address(),
            "MAC Address": self.get_mac_address()
        }