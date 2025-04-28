import sys
import os
from .services.vpn import VPNManager
from .services.wifi import WifiManager
from .services.ethernet import EthernetService
from .services.audio import AudioManager
from .services.systemd import get_service_status, start_service, stop_service, restart_service, get_service_details
import getpass

COYOTE_SERVICE_NAME = "coyote.service"

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_menu():
    """Print the main menu options."""
    print("=" * 50)
    print("       Coyote System Manager - Terminal Edition       ")
    print("=" * 50)
    print("1. Network Status")
    print("2. Audio Devices")
    print("3. Service Management")
    print("q. Quit")
    print("=" * 50)
    return input("Select an option: ")

def show_network_status():
    """Display network status information."""
    clear_screen()
    print("=" * 50)
    print("              Network Status                ")
    print("=" * 50)
    
    # VPN Status
    vpn_manager = VPNManager()
    vpn_status = vpn_manager.get_vpn_status()
    print(f"VPN Status: {vpn_status}")
    
    # Ethernet Status
    ethernet_service = EthernetService()
    ethernet_info = ethernet_service.get_connection_info()
    print("\nWired Network:")
    for key, value in ethernet_info.items():
        print(f"  {key}: {value}")
    
    # WiFi Status
    wifi_manager = WifiManager()
    wifi_status = wifi_manager.get_wifi_status()
    print(f"\nWiFi Status: {wifi_status}")
    
    # Current WiFi connection info
    current_wifi = wifi_manager.get_current_connection()
    if current_wifi['Status'] == 'Connected':
        print("\nConnected to WiFi network:")
        for key, value in current_wifi.items():
            print(f"  {key}: {value}")
    else:
        print("\nNot connected to any WiFi network")
    
    print("\nOptions:")
    print("1. Connect VPN")
    print("2. Disconnect VPN")
    print("3. View Available WiFi Networks")
    print("4. Connect to WiFi Network")
    print("5. Disconnect from WiFi")
    print("6. Forget WiFi Network")
    print("7. Refresh Network Status")
    print("b. Back to Main Menu")
    choice = input("\nSelect an option: ")
    
    if choice == '1':
        result = vpn_manager.connect_vpn()
        print(result)
        input("Press Enter to continue...")
        show_network_status()
    elif choice == '2':
        result = vpn_manager.disconnect_vpn()
        print(result)
        input("Press Enter to continue...")
        show_network_status()
    elif choice == '3':
        show_wifi_networks(wifi_manager)
    elif choice == '4':
        connect_to_wifi_network(wifi_manager)
    elif choice == '5':
        result = wifi_manager.disconnect()
        print(result)
        input("Press Enter to continue...")
        show_network_status()
    elif choice == '6':
        forget_wifi_network(wifi_manager)
    elif choice == '7':
        show_network_status()
    elif choice.lower() == 'b':
        return
    else:
        print("Invalid option")
        input("Press Enter to continue...")
        show_network_status()

def show_wifi_networks(wifi_manager):
    """Display available WiFi networks."""
    clear_screen()
    print("=" * 50)
    print("        Available WiFi Networks        ")
    print("=" * 50)
    print("Scanning for networks...")
    
    # Refresh the access points
    access_points = wifi_manager.get_access_points()
    
    if not access_points:
        print("No access points found")
    elif "Error" in access_points[0]:
        print(access_points[0]["Error"])
    else:
        print(f"\n{'#':<3} {'SSID':<30} {'Signal':<8} {'Security':<15}")
        print("-" * 60)
        
        # Get the list of known networks
        known_networks = wifi_manager.known_networks.keys()
        
        for idx, ap in enumerate(access_points):
            ssid = ap.get('SSID', 'Unknown')
            signal = ap.get('Signal', 'N/A')
            security = ap.get('Security', 'N/A')
            bssid = ap.get('BSSID', '')
            
            # Add an indicator for known networks
            known_marker = " [K]" if ssid in known_networks else ""
            
            # Add MAC address only if SSID is missing or empty
            if not ssid or ssid == '--':
                display_name = f"Hidden ({bssid})"
            else:
                display_name = ssid
                
            # Truncate long SSIDs
            if len(display_name) > 26:
                display_name = display_name[:23] + "..."
                
            print(f"{idx+1:<3} {display_name+known_marker:<30} {signal:<8} {security:<15}")
    
    print("\nOptions:")
    print("1. Connect to a network")
    print("2. Refresh scan")
    print("b. Back to Network Status")
    
    choice = input("\nSelect an option: ")
    
    if choice == '1':
        connect_to_wifi_network(wifi_manager, access_points)
    elif choice == '2':
        show_wifi_networks(wifi_manager)
    elif choice.lower() == 'b':
        show_network_status()
    else:
        print("Invalid option")
        input("Press Enter to continue...")
        show_wifi_networks(wifi_manager)

def connect_to_wifi_network(wifi_manager, access_points=None):
    """Connect to a WiFi network."""
    clear_screen()
    print("=" * 50)
    print("        Connect to WiFi Network        ")
    print("=" * 50)
    
    if not access_points:
        access_points = wifi_manager.get_access_points()
        
    if not access_points or "Error" in access_points[0]:
        print("No networks available to connect")
        input("Press Enter to continue...")
        show_network_status()
        return
        
    # Option 1: Select from the list of available networks
    print("\nAvailable networks:")
    for idx, ap in enumerate(access_points):
        ssid = ap.get('SSID', 'Unknown')
        bssid = ap.get('BSSID', '')
        
        # Handle hidden networks
        if not ssid or ssid == '--':
            display_name = f"Hidden ({bssid})"
        else:
            display_name = ssid
            
        print(f"{idx+1}. {display_name}")
    
    print("\nr. Refresh scan")
    print("m. Connect by manually entering network name")
    print("b. Back to Network Status")
    
    choice = input("\nSelect a network (1-{}) or option: ".format(len(access_points)))
    
    if choice.lower() == 'r':
        connect_to_wifi_network(wifi_manager)
        return
    elif choice.lower() == 'm':
        # Manual SSID entry
        ssid = input("Enter the network name (SSID): ")
        if not ssid:
            print("No network name entered")
            input("Press Enter to continue...")
            connect_to_wifi_network(wifi_manager, access_points)
            return
    elif choice.lower() == 'b':
        show_network_status()
        return
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(access_points):
                ssid = access_points[idx]['SSID']
                # Handle hidden networks that need manual SSID entry
                if not ssid or ssid == '--':
                    print("This appears to be a hidden network.")
                    ssid = input("Enter the network name (SSID): ")
                    if not ssid:
                        print("No network name entered")
                        input("Press Enter to continue...")
                        connect_to_wifi_network(wifi_manager, access_points)
                        return
            else:
                print("Invalid selection")
                input("Press Enter to continue...")
                connect_to_wifi_network(wifi_manager, access_points)
                return
        except ValueError:
            print("Invalid selection")
            input("Press Enter to continue...")
            connect_to_wifi_network(wifi_manager, access_points)
            return
    
    # Check if it's a known network
    if ssid in wifi_manager.known_networks:
        print(f"\nConnecting to known network '{ssid}'...")
        result = wifi_manager.connect_to_access_point(ssid)
        print(result)
        input("Press Enter to continue...")
        show_network_status()
        return
    
    # Ask for password
    print(f"\nConnecting to new network '{ssid}'")
    
    # Try to detect if it's an open network based on Security field
    is_open = False
    for ap in access_points:
        if ap.get('SSID') == ssid and ap.get('Security', '').lower() in ['--', 'none', '']:
            is_open = True
            break
            
    if is_open:
        print("This appears to be an open network. Attempting to connect without password...")
        result = wifi_manager.connect_to_access_point(ssid, None)
    else:
        password = getpass.getpass("Enter network password: ")
        if not password:
            print("No password entered, attempting to connect as open network...")
            result = wifi_manager.connect_to_access_point(ssid, None)
        else:
            result = wifi_manager.connect_to_access_point(ssid, password)
    
    print(result)
    input("Press Enter to continue...")
    show_network_status()

def forget_wifi_network(wifi_manager):
    """Remove a WiFi network from saved networks."""
    clear_screen()
    print("=" * 50)
    print("        Forget WiFi Network        ")
    print("=" * 50)
    
    known_networks = list(wifi_manager.known_networks.keys())
    
    if not known_networks:
        print("No saved networks found")
        input("Press Enter to continue...")
        show_network_status()
        return
    
    print("\nSaved networks:")
    for idx, ssid in enumerate(known_networks):
        print(f"{idx+1}. {ssid}")
    
    print("\nb. Back to Network Status")
    
    choice = input("\nSelect a network to forget (1-{}) or option: ".format(len(known_networks)))
    
    if choice.lower() == 'b':
        show_network_status()
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(known_networks):
            ssid = known_networks[idx]
            
            confirm = input(f"Are you sure you want to forget network '{ssid}'? (y/n): ")
            if confirm.lower() == 'y':
                result = wifi_manager.forget_network(ssid)
                print(result)
            else:
                print("Operation cancelled")
            
            input("Press Enter to continue...")
            show_network_status()
        else:
            print("Invalid selection")
            input("Press Enter to continue...")
            forget_wifi_network(wifi_manager)
    except ValueError:
        print("Invalid selection")
        input("Press Enter to continue...")
        forget_wifi_network(wifi_manager)

def show_audio_devices():
    """Display audio device information."""
    clear_screen()
    print("=" * 50)
    print("              Audio Devices                ")
    print("=" * 50)
    
    # Audio Output Devices
    devices = AudioManager.get_audio_output_devices()
    print("Audio Output Devices:")
    if not devices:
        print("  No audio devices found")
    else:
        for device in devices:
            print(f"  {device['index']}: {device['name']} (Volume: {device['volume']}%)")
    
    # Microphones
    mics = AudioManager.get_usb_microphones()
    print("\nMicrophones:")
    if not mics:
        print("  No microphones found")
    else:
        for mic in mics:
            print(f"  {mic['index']}: {mic['name']} (Volume: {mic['volume']}%)")
    
    print("\nOptions:")
    print("1. Refresh Audio Devices")
    print("b. Back to Main Menu")
    choice = input("\nSelect an option: ")
    
    if choice == '1':
        show_audio_devices()
    elif choice.lower() == 'b':
        return
    else:
        print("Invalid option")
        input("Press Enter to continue...")
        show_audio_devices()

def show_service_management():
    """Display service management options."""
    clear_screen()
    print("=" * 50)
    print("            Service Management              ")
    print("=" * 50)
    
    status = get_service_status(COYOTE_SERVICE_NAME)
    print(f"Service: {COYOTE_SERVICE_NAME}")
    print(f"Status: {status}")
    
    # Get more detailed information about the service
    print("\nService Details:")
    details = get_service_details(COYOTE_SERVICE_NAME)
    
    # Print only the first few lines to keep it readable
    detail_lines = details.splitlines()
    for i, line in enumerate(detail_lines[:10]):  # Show first 10 lines max
        print(f"  {line}")
    if len(detail_lines) > 10:
        print(f"  ... and {len(detail_lines) - 10} more lines")
    
    print("\nOptions:")
    print("1. Start Service")
    print("2. Stop Service")
    print("3. Restart Service")
    print("4. View Full Service Details")
    print("5. Refresh Status")
    print("b. Back to Main Menu")
    choice = input("\nSelect an option: ")
    
    if choice == '1':
        success, message = start_service(COYOTE_SERVICE_NAME)
        print(message)
        if not success:
            print("\nTroubleshooting tips:")
            print("- Check if the service file is properly configured")
            print("- Verify the ExecStart path in the service file")
            print("- Look for any dependency issues in the service")
            print("- Check the full logs using journalctl -u coyote.service")
        input("Press Enter to continue...")
        show_service_management()
    elif choice == '2':
        success, message = stop_service(COYOTE_SERVICE_NAME)
        print(message)
        input("Press Enter to continue...")
        show_service_management()
    elif choice == '3':
        success, message = restart_service(COYOTE_SERVICE_NAME)
        print(message)
        input("Press Enter to continue...")
        show_service_management()
    elif choice == '4':
        clear_screen()
        print("=" * 50)
        print(f"     Full Service Details for {COYOTE_SERVICE_NAME}     ")
        print("=" * 50)
        print(details)
        print("\n" + "=" * 50)
        input("Press Enter to return...")
        show_service_management()
    elif choice == '5':
        show_service_management()
    elif choice.lower() == 'b':
        return
    else:
        print("Invalid option")
        input("Press Enter to continue...")
        show_service_management()

def main():
    """Main application loop."""
    try:
        while True:
            clear_screen()
            choice = print_menu()
            
            if choice == '1':
                show_network_status()
            elif choice == '2':
                show_audio_devices()
            elif choice == '3':
                show_service_management()
            elif choice.lower() == 'q':
                clear_screen()
                print("Thank you for using Coyote System Manager!")
                sys.exit(0)
            else:
                print("Invalid option")
                input("Press Enter to continue...")
    except KeyboardInterrupt:
        clear_screen()
        print("Program terminated by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()