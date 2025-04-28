![Coyote Image](coyote.png)

# Coyote Interactive

## Overview
A modular system for interactive coyote behaviors and communications.

## Features
- **LEDs**: Control of LED patterns.
- **Buttons**: Handling of button events.
- **Audio to Text**: Continuous transcription using whisper-stream.
- **Television Comments**: AI-powered commentary on television content.
- **Conversation Data**: Log storage for interactions.
  - **Conversation Archiving**: Automatic timestamped archiving of conversation history.
- **Talk with Person**: Captures intercom speech and manages the conversation flow with AI.
- **Wake/Sleep Modes**: System operates in different modes based on switch position.
  - **BOOM Feature**: Press both buttons simultaneously in sleep mode to archive the current conversation.
- **Auto-start on Boot**: System automatically starts on boot using systemd user services.
- **System Manager**: Terminal-based utility to manage network, audio settings, and service control.

## Setup
- Install dependencies (Python, gpiozero, whisper-stream, etc.).
- Configure GPIO pins and other settings in config files.
- Run system configuration checks with the manager's setup.py script.

## Usage
### Running Manually
- `python coyote.py`
- `./manager/run_manager.py` (for the system manager utility)

### Auto-start Configuration
The system is configured to automatically start on boot using systemd:
- Service runs in a Byobu session for easy attachment/detachment
- Full environment context is maintained (Python virtual environment, working directory, etc.)
- Environment variables for speech models are properly configured
- To attach to the running session: `byobu attach -t coyote_session` (or use alias `b`)
- To check service status: `systemctl --user status coyote.service`

#### Setting Up Auto-start (Systemd Service)

1. **Copy the service file to systemd user directory**:
   ```bash
   mkdir -p ~/.config/systemd/user/
   cp /home/robot/coyote_interactive/coyote.service ~/.config/systemd/user/
   ```

2. **Reload systemd configuration**:
   ```bash
   systemctl --user daemon-reload
   ```

3. **Enable the service to start at boot**:
   ```bash
   systemctl --user enable coyote.service
   ```

4. **Enable lingering (to start service without user login)**:
   ```bash
   sudo loginctl enable-linger $USER
   ```

5. **Start the service immediately**:
   ```bash
   systemctl --user start coyote.service
   ```

6. **Create convenient alias to attach to session** (add to ~/.bashrc):
   ```bash
   echo "alias b='byobu attach -t coyote_session'" >> ~/.bashrc
   source ~/.bashrc
   ```

7. **Check service status**:
   ```bash
   systemctl --user status coyote.service
   ```

**Note**: The service file (`coyote.service`) must be located at `~/.config/systemd/user/coyote.service` to function properly. A template is provided in the project root directory.

## System Manager

The Coyote System Manager is a terminal-based utility for monitoring and managing system components:

### Features
- Network monitoring (WiFi, Ethernet, VPN)
- Audio device management
- Coyote service control (start/stop/restart)

### Installation
There are two ways to use the System Manager:

1. **Run directly** (recommended):
   ```bash
   cd ~/coyote_interactive/manager
   ./run_manager.py
   ```

2. **Install as a package**:
   ```bash
   cd ~/coyote_interactive
   pip install -e ./manager
   coyote-manager
   ```

### System Configuration
The manager includes a setup script to configure system permissions and check dependencies:

```bash
cd ~/coyote_interactive/manager
python setup.py check_system
```

This script will:
- Configure sudo permissions for NetworkManager WiFi operations
- Set up systemd user lingering
- Install coyote.service if needed
- Check for required system dependencies

For more details, see the [manager README](manager/README.md).

## Operation
- **Wake Mode**: System actively responds to button presses for TV or person interactions.
  - Conversation directory is checked/created before each interaction to ensure stability.
- **Sleep Mode**: System is idle but monitors for the special "BOOM" button combination.
  - Pressing both TV and person buttons archives the current conversation with a timestamp.
- **Conversation Management**: 
  - Conversations are stored in JSON format
  - Archives are automatically named with timestamps (e.g. `conversation_YYYYMMDD_HHMMSS.json`)

## Demonstration Video

[![Watch on YouTube](https://img.shields.io/badge/Watch%20on-YouTube-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=pncuq-U_tuU)  
[![Video Thumbnail](https://img.youtube.com/vi/pncuq-U_tuU/0.jpg)](https://www.youtube.com/watch?v=pncuq-U_tuU)

