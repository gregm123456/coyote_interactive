# Coyote System Manager

This project is a utility application designed to manage and display various network and audio device statuses. It provides a user-friendly terminal interface to monitor VPN connections, wireless access points, wired network status, USB microphones, audio output devices, and the management of the `coyote.service`.

## Features

- **Network Management**: 
  - View and manage VPN status.
  - Display wireless access point names and statuses.
  - Monitor wired network connections.

- **Audio Management**: 
  - List USB microphone names and their volume levels.
  - Display audio output device names and their volume levels.

- **Service Management**: 
  - Show the status of the `coyote.service`.
  - Provide options to start, stop, and restart the service.

## Directory Structure

- `src/main.py`: Entry point of the application.
- `src/ui/`: Contains the user interface components.
  - `app.py`: Main application class.
  - `screens/`: Different screens for managing network, audio, and services.
  - `widgets/`: Custom widgets for displaying information.
- `src/services/`: Contains service management functionalities.
  - `vpn.py`: VPN connection management.
  - `wifi.py`: Wi-Fi network management.
  - `ethernet.py`: Wired network management.
  - `audio.py`: Audio device management.
  - `systemd.py`: System service management.
- `src/utils/`: Utility functions for various tasks.
- `tests/`: Unit tests for the application functionalities.
- `setup.py`: Setup script for the project.
- `check_system.py`: Script to verify system configuration.
- `run_manager.py`: Standalone script to run the manager application.

## Installation

There are two ways to install and run the Coyote System Manager:

### Method 1: Run the standalone script (Recommended)

1. Navigate to the manager directory:
   ```
   cd ~/coyote_interactive/manager
   ```

2. Make sure the run_manager.py script is executable:
   ```
   chmod +x run_manager.py
   ```

3. Run the application:
   ```
   ./run_manager.py
   ```

### Method 2: Install as a package

1. Navigate to the coyote_interactive directory:
   ```
   cd ~/coyote_interactive
   ```

2. Install the package in development mode:
   ```
   pip install -e ./manager
   ```

3. Run the application using the entry point:
   ```
   coyote-manager
   ```

## System Configuration with setup.py

The `setup.py` script is responsible for verifying and configuring various system requirements needed for the Coyote Manager to function correctly. You should run this script when:

- Setting up the application for the first time
- After system updates that might affect services or permissions
- If you encounter permission issues with WiFi or system services
- When experiencing problems with the coyote.service

### When to run setup.py:

- During initial installation
- When troubleshooting permissions issues
- After upgrading your operating system
- If NetworkManager or systemd configurations have changed

### What setup.py does:

- Checks and configures sudo permissions for NetworkManager WiFi operations
- Verifies the coyote.service file is properly installed
- Enables systemd user lingering (allows services to run without login)
- Verifies required system dependencies are installed
- Sets up proper sudo permissions for systemctl commands

### How to run setup.py:

You can run the setup script in two ways:

1. Directly as a Python script:
   ```
   cd ~/coyote_interactive/manager
   python setup.py check_system
   ```

2. During package installation (will run automatically):
   ```
   cd ~/coyote_interactive
   pip install -e ./manager
   ```

Follow the prompts and answer 'y' when asked to configure system settings. Some operations may require sudo privileges.

### Verifying Configuration Only:

If you just want to check your system configuration without making any changes:

```
cd ~/coyote_interactive/manager
python check_system.py
```

This will run all system checks and report any issues without modifying your system.

## First Run Experience

When running the Coyote System Manager for the first time, you'll see a terminal-based menu with the following options:

1. **Network Status**: View and manage network connections
2. **Audio Devices**: Manage audio input/output devices
3. **Service Management**: Control the coyote.service
q. **Quit**: Exit the application

### Network Status

This section displays:
- Current VPN connection status
- Wired network details (interface, IP address, MAC address)
- Wi-Fi status and connection details

Options include:
- Connect/disconnect VPN
- View available Wi-Fi networks
- Connect to a Wi-Fi network
- Disconnect from Wi-Fi
- Forget saved Wi-Fi networks

### Audio Devices

This section displays:
- Audio output devices with volume levels
- USB microphones with volume levels

Options include:
- Refresh the audio device list

### Service Management

This section displays:
- Status of the coyote.service
- Service details

Options include:
- Start the service
- Stop the service
- Restart the service
- View full service details

## System Requirements and Configuration

The manager requires several system configurations to work properly:

1. **User-level Systemd Service**: The application manages `coyote.service` as a user-level systemd service. This requires:
   - The service file to be installed in `~/.config/systemd/user/`
   - User lingering enabled to allow services to run without active login sessions

2. **System Dependencies**:
   - Python 3.8 or higher
   - PulseAudio for audio device management
   - NetworkManager for Wi-Fi management
   - SystemD for service management

## Troubleshooting

If you encounter issues running the manager:

1. **Import errors**: Make sure you're running the application from the correct directory or that the package is properly installed.

2. **Permission issues**: Some network and service commands might require sudo privileges. The application will inform you if elevated permissions are needed.

3. **Missing dependencies**: If you see errors related to missing modules, install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. **Service control errors**: Verify that the coyote.service exists in the system and the current user has permissions to control it.

## Usage

Once the application is running, navigate through the menu options by typing the number corresponding to your choice and pressing Enter.

To exit any screen, type 'b' to go back to the main menu. To quit the application, type 'q' at the main menu.
