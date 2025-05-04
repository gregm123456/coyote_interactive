import getpass
from ...utils.terminal import clear_screen
from ...services.vpn import VPNManager
from ...services.wifi import WifiManager
from ...services.ethernet import EthernetService

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