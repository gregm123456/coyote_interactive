from ...utils.terminal import clear_screen
from ...services.audio import AudioManager

def show_audio_devices():
    """Display audio device information."""
    while True:
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
        print("2. Select Output Device")
        print("3. Select Input Device")
        print("b. Back to Main Menu")
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            continue  # Refresh and stay in this screen
        elif choice == '2':
            # Go to output device selection
            select_audio_device(devices, is_output=True)
            # After returning, don't exit but loop back to this screen
            continue
        elif choice == '3':
            # Go to input device selection
            select_audio_device(mics, is_output=False)
            # After returning, don't exit but loop back to this screen
            continue
        elif choice.lower() == 'b':
            return  # Only exit to main menu when explicitly choosing 'b'
        else:
            print("Invalid option")
            input("Press Enter to continue...")
            # Invalid choice, stay in this screen
            continue

def select_audio_device(devices, is_output=True):
    """Select an audio device to adjust volume."""
    while True:
        clear_screen()
        device_type = "Output Device" if is_output else "Input Device"
        print("=" * 50)
        print(f"              Select {device_type}                ")
        print("=" * 50)
        
        if not devices:
            print(f"  No {device_type.lower()}s found")
            input("Press Enter to continue...")
            return
        
        # Display devices
        for device in devices:
            print(f"  {device['index']}: {device['name']} (Volume: {device['volume']}%)")
        
        print("\nEnter the index of the device you want to adjust or 'b' to go back:")
        choice = input("> ")
        
        if choice.lower() == 'b':
            return  # Return to the audio devices screen
        
        # Validate input and find selected device
        selected_device = None
        device_index = -1 # Initialize with an invalid index
        try:
            device_index = int(choice)
        except ValueError:
            print("Invalid input. Please enter a number or 'b'.")
            input("Press Enter to continue...")
            continue  # Stay in the device selection screen

        # Find the device after successful conversion
        for device in devices:
            if device['index'] == device_index:
                selected_device = device
                break
                
        if selected_device is None:
            print("No device with that index found.")
            input("Press Enter to continue...")
            continue  # Stay in the device selection screen
            
        # Show volume control for selected device (moved outside the try block)
        adjust_device_volume(selected_device, is_output)
        # After volume adjustment, loop back to device selection
        continue

def adjust_device_volume(device, is_output=True):
    """Control volume of selected audio device."""
    while True:
        clear_screen()
        device_type = "Output Device" if is_output else "Input Device"
        print("=" * 50)
        print(f"              Adjust {device_type} Volume                ")
        print("=" * 50)
        print(f"Device: {device['name']} (ID: {device['index']})")
        
        # Get current volume
        current_volume = AudioManager.get_volume(device['index'], is_sink=is_output)
        current_step = int(round(current_volume / 10))
        
        # Show volume bar - Use ASCII characters for broader compatibility
        volume_bar = "#" * current_step + "-" * (10 - current_step)
        print(f"Current volume: {current_volume}%")
        print(f"[{volume_bar}] {current_volume}%")
        
        print("\nOptions:")
        print("0-9: Set volume to 0%-90%")
        print("f: Full volume (100%)")
        print("u: Volume up by 10%")
        print("d: Volume down by 10%")
        print("r: Refresh")
        print("b: Back to device selection")
        
        choice = input("\nEnter your choice: ")
        
        if choice in "0123456789":
            # Set volume to 0-90%
            step = int(choice)
            volume = AudioManager.set_volume_step(device['index'], step, is_sink=is_output)
            device['volume'] = volume
        elif choice.lower() == 'f':
            # Set to full volume (100%)
            volume = AudioManager.set_volume_step(device['index'], 10, is_sink=is_output)
            device['volume'] = volume
        elif choice.lower() == 'u':
            # Increase volume
            volume = AudioManager.increment_volume(device['index'], is_sink=is_output)
            device['volume'] = volume
        elif choice.lower() == 'd':
            # Decrease volume
            volume = AudioManager.decrement_volume(device['index'], is_sink=is_output)
            device['volume'] = volume
        elif choice.lower() == 'r':
            # Just refresh the display
            continue
        elif choice.lower() == 'b':
            # Go back to device selection
            return
        else:
            print("Invalid option")
            input("Press Enter to continue...")
