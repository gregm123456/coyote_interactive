import sys
import os
from .utils.terminal import clear_screen
from .services.systemd import get_service_status
from .ui.screens import (
    show_network_status,
    show_audio_devices, 
    show_service_management,
    show_television_transcript,
    show_dialogue
)

COYOTE_SERVICE_NAME = "coyote.service"

def print_menu():
    """Print the main menu options."""
    # Get the service status
    status = get_service_status(COYOTE_SERVICE_NAME)
    
    # Determine the title based on status
    if status == 'active':
        title = "Coyote System Manager - Service Up"
    else:
        title = "Coyote System Manager - Service Down"
        
    # Center the title
    title_line = title.center(50)
    
    print("=" * 50)
    print(title_line)  # Use the dynamic title
    print("=" * 50)
    print("1. Network Status")
    print("2. Audio Devices")
    print("3. Service Management")
    print("4. Television Transcript")
    print("5. Dialogue")
    print("q. Quit")
    print("=" * 50)
    return input("Select an option: ")

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
            elif choice == '4':
                show_television_transcript()
            elif choice == '5':
                show_dialogue()
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
