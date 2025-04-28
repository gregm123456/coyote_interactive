import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VPNManager:
    def __init__(self, service_name="openvpn@sonic_client.service"):
        """
        Initializes the VPNManager for a specific systemd service.

        Args:
            service_name (str): The full name of the systemd service for the VPN connection 
                                (e.g., 'openvpn@sonic_client.service').
        """
        self.service_name = service_name
        self.vpn_status = self.get_vpn_status()
        logging.info(f"VPNManager initialized for service: {self.service_name}. Initial status: {self.vpn_status}")

    def _run_systemctl_command(self, command: list) -> tuple[bool, str]:
        """Helper function to run systemctl commands."""
        try:
            logging.debug(f"Running systemctl command: {' '.join(command)}")
            result = subprocess.run(['sudo', 'systemctl'] + command, capture_output=True, text=True, check=False)
            logging.debug(f"Command stdout: {result.stdout.strip()}")
            logging.debug(f"Command stderr: {result.stderr.strip()}")
            logging.debug(f"Command return code: {result.returncode}")
            
            # check=False means we need to check returncode manually
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                # Try to provide a more specific error if possible
                if "Unit {} not found.".format(self.service_name) in result.stderr:
                     error_msg = f"Error: Service '{self.service_name}' not found."
                elif "inactive" in result.stdout and command[0] == 'is-active': # is-active returns non-zero for inactive
                    return False, "inactive" # Special case for is-active
                else:
                    error_msg = f"Error running systemctl {' '.join(command)}: {result.stderr.strip() or result.stdout.strip()}"
                
                logging.error(error_msg)
                return False, error_msg
        except FileNotFoundError:
            error_msg = "Error: 'sudo' or 'systemctl' command not found. Ensure systemd is installed and accessible."
            logging.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            logging.exception(error_msg) # Log full traceback for unexpected errors
            return False, error_msg

    def get_vpn_status(self) -> str:
        """
        Checks the status of the configured systemd VPN service.

        Returns:
            str: "Connected" if the service is active, "Disconnected" if inactive, 
                 or an error message.
        """
        success, output = self._run_systemctl_command(['is-active', self.service_name])
        
        if success and output == "active":
            self.vpn_status = "Connected"
            logging.info(f"VPN status for {self.service_name}: Connected")
            return "Connected"
        elif not success and output == "inactive": # Handled special case from _run_systemctl_command
             self.vpn_status = "Disconnected"
             logging.info(f"VPN status for {self.service_name}: Disconnected")
             return "Disconnected"
        else:
            # Output contains the error message from _run_systemctl_command
            self.vpn_status = f"Error: {output}" 
            logging.warning(f"VPN status check failed for {self.service_name}: {output}")
            return self.vpn_status # Return the error message

    def connect_vpn(self) -> str:
        """
        Starts the configured systemd VPN service.

        Returns:
            str: A message indicating success or failure.
        """
        current_status = self.get_vpn_status()
        if current_status == "Connected":
            msg = f"VPN service '{self.service_name}' is already connected."
            logging.info(msg)
            return msg
        elif current_status.startswith("Error"):
             msg = f"Cannot connect VPN: Previous status check failed: {current_status}"
             logging.error(msg)
             return msg


        logging.info(f"Attempting to connect VPN service: {self.service_name}")
        success, output = self._run_systemctl_command(['start', self.service_name])
        
        if success:
            # Verify status after attempting start
            self.vpn_status = self.get_vpn_status() # Update status
            if self.vpn_status == "Connected":
                 msg = f"VPN service '{self.service_name}' started successfully."
                 logging.info(msg)
                 return msg
            else:
                 # This case might happen if the service starts but immediately fails
                 msg = f"VPN service '{self.service_name}' started but is not active. Status: {self.vpn_status}. Check service logs ('journalctl -u {self.service_name}') for details."
                 logging.warning(msg)
                 return msg
        else:
            self.vpn_status = f"Error: {output}" # Update status with error
            msg = f"Failed to start VPN service '{self.service_name}'. Error: {output}"
            logging.error(msg)
            return msg

    def disconnect_vpn(self) -> str:
        """
        Stops the configured systemd VPN service.

        Returns:
            str: A message indicating success or failure.
        """
        current_status = self.get_vpn_status()
        if current_status == "Disconnected":
            msg = f"VPN service '{self.service_name}' is already disconnected."
            logging.info(msg)
            return msg
        elif current_status.startswith("Error"):
             msg = f"Cannot disconnect VPN: Previous status check failed: {current_status}"
             logging.error(msg)
             return msg

        logging.info(f"Attempting to disconnect VPN service: {self.service_name}")
        success, output = self._run_systemctl_command(['stop', self.service_name])
        
        if success:
             # Verify status after attempting stop
            self.vpn_status = self.get_vpn_status() # Update status
            if self.vpn_status == "Disconnected":
                 msg = f"VPN service '{self.service_name}' stopped successfully."
                 logging.info(msg)
                 return msg
            else:
                 # This might happen if the stop command succeeds but the service is still somehow active or in error
                 msg = f"VPN service '{self.service_name}' stop command issued, but current status is: {self.vpn_status}."
                 logging.warning(msg)
                 return msg
        else:
            self.vpn_status = f"Error: {output}" # Update status with error
            msg = f"Failed to stop VPN service '{self.service_name}'. Error: {output}"
            logging.error(msg)
            return msg

    def get_service_details(self) -> dict:
        """
        Retrieves details about the configured systemd VPN service.

        Returns:
            dict: A dictionary containing the service name and its current status.
                  Returns an error message in the 'status' field if retrieval fails.
        """
        status = self.get_vpn_status() # Use the existing method to get current status
        details = {
            'service_name': self.service_name,
            'status': status 
        }
        logging.info(f"Retrieving details for {self.service_name}: {details}")
        return details

# Example Usage (optional, for testing)
if __name__ == '__main__':
    vpn_manager = VPNManager() # Uses default 'openvpn@sonic_client.service'
    
    print("--- Initial Status ---")
    print(f"Service: {vpn_manager.service_name}")
    print(f"Status: {vpn_manager.get_vpn_status()}")

    # print("\n--- Attempting to Connect ---")
    # print(vpn_manager.connect_vpn())
    # print(f"Status after connect attempt: {vpn_manager.get_vpn_status()}")

    # print("\n--- Attempting to Disconnect ---")
    # print(vpn_manager.disconnect_vpn())
    # print(f"Status after disconnect attempt: {vpn_manager.get_vpn_status()}")

    print("\n--- Service Details ---")
    print(vpn_manager.get_service_details())