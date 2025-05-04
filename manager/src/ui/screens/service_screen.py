from ...utils.terminal import clear_screen
from ...services.systemd import get_service_status, start_service, stop_service
from ...services.systemd import restart_service, get_service_details

COYOTE_SERVICE_NAME = "coyote.service"

def show_service_management():
    """Display service management options."""
    while True:  # Add loop for refresh/retry
        clear_screen()
        print("=" * 50)
        print("            Service Management              ")
        print("=" * 50)

        status = get_service_status(COYOTE_SERVICE_NAME)
        print(f"Service: {COYOTE_SERVICE_NAME}")
        print(f"Status: {status}")

        # Get detailed information to extract the 'Active' line
        details = get_service_details(COYOTE_SERVICE_NAME)
        detail_lines = details.splitlines()
        active_line = ""
        for line in detail_lines:
            stripped_line = line.strip()
            if stripped_line.startswith("Active:"):
                active_line = stripped_line  # Keep the whole line
                break

        if active_line:
            # Indent the active line slightly for clarity
            print(f"  {active_line}")
        elif status != 'inactive':  # Only show if not inactive and active line missing
            print("  (Could not retrieve running time details)")

        print("\nOptions:")
        print("1. Start Service")
        print("2. Stop Service")
        print("3. Restart Service")
        print("4. Refresh Status")  # Renumbered
        print("b. Back to Main Menu")
        choice = input("\nSelect an option: ")

        if choice == '1':
            success, message = start_service(COYOTE_SERVICE_NAME)
            print(message)
            if not success:
                print("\nTroubleshooting tips:")
                print("- Check service file, ExecStart path, dependencies.")
                print("- Check logs: journalctl --user -u coyote.service")
            input("Press Enter to continue...")
            # Loop continues, effectively refreshing
        elif choice == '2':
            success, message = stop_service(COYOTE_SERVICE_NAME)
            print(message)
            input("Press Enter to continue...")
            # Loop continues
        elif choice == '3':
            success, message = restart_service(COYOTE_SERVICE_NAME)
            print(message)
            input("Press Enter to continue...")
            # Loop continues
        elif choice == '4':
            # Just continue the loop to refresh
            continue
        elif choice.lower() == 'b':
            return  # Exit the loop and return to main menu
        else:
            print("Invalid option")
            input("Press Enter to continue...")
            # Loop continues