from typing import List, Dict
import subprocess
import os
import json

class WifiManager:
    def __init__(self):
        self.wifi_status = self.get_wifi_status()
        self.access_points = self.get_access_points()
        # Path to store known networks and their credentials
        self.known_networks_file = os.path.expanduser("~/.config/coyote/known_networks.json")
        self.known_networks = self._load_known_networks()
        
    def _load_known_networks(self) -> Dict[str, str]:
        """Load known networks from the config file."""
        if not os.path.exists(self.known_networks_file):
            directory = os.path.dirname(self.known_networks_file)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            return {}
            
        try:
            with open(self.known_networks_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading known networks: {e}")
            return {}
    
    def _save_known_networks(self):
        """Save known networks to the config file."""
        try:
            with open(self.known_networks_file, 'w') as f:
                json.dump(self.known_networks, f)
        except Exception as e:
            print(f"Error saving known networks: {e}")

    def get_wifi_status(self) -> str:
        try:
            result = subprocess.run(['nmcli', 'radio', 'wifi'], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error retrieving WiFi status: {e}"

    def get_access_points(self) -> List[Dict[str, str]]:
        """Get list of available WiFi access points with proper SSIDs."""
        try:
            # Use nmcli with specific format to get clear SSID information
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,BSSID,CHAN', 'device', 'wifi', 'list'], 
                capture_output=True, 
                text=True
            )
            
            access_points = []
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) >= 4:
                        ssid = parts[0]
                        # Skip networks with empty SSIDs
                        if not ssid:
                            continue
                            
                        signal = parts[1]
                        security = parts[2] if parts[2] else "Open"
                        bssid = parts[3]  # MAC address
                        channel = parts[4] if len(parts) > 4 else "Unknown"
                        
                        access_points.append({
                            'SSID': ssid,
                            'Signal': signal,
                            'Security': security,
                            'BSSID': bssid,
                            'Channel': channel
                        })
            
            # If tabular format didn't work, try the default output format
            if not access_points:
                # Alternative approach using standard output format
                result = subprocess.run(['nmcli', 'device', 'wifi', 'list'], capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')[1:]  # Skip header line
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 8:
                        # Determine how many parts make up the SSID (which may contain spaces)
                        security_index = -1
                        for i, part in enumerate(parts):
                            if part in ['WPA1', 'WPA2', 'WEP', '--']:
                                security_index = i
                                break
                        
                        if security_index > 1:
                            # In-use marker (*) may be present as first column
                            start_idx = 1 if parts[0] == '*' else 0
                            ssid = ' '.join(parts[start_idx:security_index])
                            bssid = parts[security_index - 1]
                            signal = parts[security_index + 1]
                            security = parts[security_index]
                            
                            access_points.append({
                                'SSID': ssid,
                                'Signal': signal,
                                'Security': security,
                                'BSSID': bssid
                            })
            
            return access_points
        except Exception as e:
            return [{"Error": f"Error retrieving access points: {e}"}]

    def connect_to_access_point(self, ssid: str, password: str = None) -> str:
        """
        Connect to a WiFi access point using sudo if necessary.
        If password is None, attempts to use stored password for known network.
        """
        # Check if this is a known network
        if password is None and ssid in self.known_networks:
            password = self.known_networks[ssid]
            
        try:
            # First, get the SSID of the currently connected network for verification later
            original_connection = self.get_current_connection()
            original_ssid = original_connection.get('SSID')
            
            # Attempt to connect
            if password:
                # Use sudo for the connection with password command
                cmd = ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password]
                print(f"Connecting to {ssid} with provided password...")
                result = subprocess.run(cmd, capture_output=True, text=True)
            else:
                # Try to connect without a password (for open networks)
                cmd = ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid]
                print(f"Connecting to {ssid} (open network)...")
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Wait for the connection to stabilize
            import time
            time.sleep(3)  # Give NetworkManager time to establish the connection
            
            # Verify that we're actually connected to the new network
            new_connection = self.get_current_connection()
            new_ssid = new_connection.get('SSID')
            
            if new_ssid == ssid:
                # True success - connected to the requested network
                if password:
                    self.known_networks[ssid] = password
                    self._save_known_networks()
                elif result.returncode == 0:  # Open network, successful connection
                    self.known_networks[ssid] = ""
                    self._save_known_networks()
                
                return f"Successfully connected to {ssid}."
            else:
                # Failed to connect but command returned success
                failed_reason = ""
                if "Error" in result.stderr:
                    failed_reason = result.stderr.strip()
                elif "Error" in result.stdout:
                    failed_reason = result.stdout.strip()
                    
                return f"Failed to connect to {ssid}. Still connected to {new_ssid or 'unknown network'}. {failed_reason}"
                
        except Exception as e:
            return f"Error connecting to {ssid}: {e}"

    def disconnect(self) -> str:
        try:
            # Get the active WiFi interface
            result = subprocess.run(['nmcli', '-t', '-f', 'DEVICE', 'connection', 'show', '--active'], 
                                  capture_output=True, text=True)
            
            wifi_interfaces = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('wlan') or line.startswith('wi-fi'):
                    wifi_interfaces.append(line.split(':')[0])
            
            if not wifi_interfaces:
                return "No active WiFi connection found."
            
            # Disconnect from all active WiFi interfaces
            for interface in wifi_interfaces:
                cmd = ['sudo', 'nmcli', 'device', 'disconnect', interface]
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            return "Disconnected successfully."
        except Exception as e:
            return f"Error disconnecting: {e}"
    
    def get_current_connection(self) -> Dict[str, str]:
        """Get information about the current WiFi connection."""
        try:
            # Check for active WiFi connections using nmcli
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'NAME,DEVICE,TYPE,ACTIVE', 'connection', 'show'], 
                capture_output=True, text=True
            )
            
            # First pass: look for active WiFi connections
            connection_name = None
            device_name = None
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    # Check if it's an active WiFi connection (fields: name:device:type:active)
                    if len(parts) >= 4 and parts[2] in ['wifi', '802-11-wireless'] and parts[3] == 'yes':
                        connection_name = parts[0]  # This is the connection profile name
                        device_name = parts[1]  # Interface name
                        break
            
            if not connection_name:
                return {'Status': 'Not Connected'}
            
            # Get the actual WiFi SSID which may be different from the connection name
            # Use 'nmcli -g 802-11-wireless.ssid connection show <connection_name>'
            ssid_cmd = subprocess.run(
                ['nmcli', '-g', '802-11-wireless.ssid', 'connection', 'show', connection_name],
                capture_output=True, text=True
            )
            
            actual_ssid = ssid_cmd.stdout.strip()
            
            # If that didn't work, try another approach by looking at the active device
            if not actual_ssid:
                wifi_details = subprocess.run(
                    ['nmcli', '-f', 'ACTIVE,SSID', 'device', 'wifi', 'list'],
                    capture_output=True, text=True
                )
                
                for line in wifi_details.stdout.strip().split('\n'):
                    if '*' in line:  # The active connection is marked with *
                        parts = line.split()
                        if len(parts) >= 2:
                            # The SSID might contain spaces, so join all parts except the first few
                            actual_ssid = ' '.join(parts[1:]).strip()
                            break
            
            # Initialize connection info with basic details
            info = {
                'ConnectionName': connection_name,
                'SSID': actual_ssid or connection_name,  # Fall back to connection name if SSID not found
                'Interface': device_name,
                'Status': 'Connected'
            }
            
            # Extract IP and other network information
            ip_cmd = subprocess.run(
                ['ip', 'addr', 'show', device_name],
                capture_output=True, text=True
            )
            
            # Parse IP address
            for line in ip_cmd.stdout.strip().split('\n'):
                if 'inet ' in line:
                    # Extract IP address/netmask (format: inet 192.168.1.100/24)
                    ip_with_mask = line.strip().split()[1]
                    info['IP'] = ip_with_mask
                    break
            
            # Get signal strength for current connection
            signal_cmd = subprocess.run(
                ['nmcli', '-f', 'IN-USE,SIGNAL', 'device', 'wifi', 'list'],
                capture_output=True, text=True
            )
            
            for line in signal_cmd.stdout.strip().split('\n'):
                if '*' in line:  # The active connection is marked with *
                    parts = line.split()
                    if len(parts) >= 2:
                        info['Signal'] = parts[1] + '%'
                    break
                    
            return info
        except Exception as e:
            return {'Status': f'Error: {e}'}
    
    def forget_network(self, ssid: str) -> str:
        """Remove a network from known networks."""
        if ssid in self.known_networks:
            del self.known_networks[ssid]
            self._save_known_networks()
            
            # Also delete the connection from NetworkManager
            try:
                cmd = ['sudo', 'nmcli', 'connection', 'delete', ssid]
                subprocess.run(cmd, capture_output=True, text=True)
                return f"Network {ssid} forgotten."
            except Exception as e:
                return f"Error removing network {ssid} from system: {e}"
        else:
            return f"Network {ssid} not found in known networks."