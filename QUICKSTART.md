# Quick Start Guide - Coyote Interactive on Raspberry Pi

## Fresh Installation

```bash
cd ~/coyote_interactive
./install.sh
```

The automated script will install everything. Follow the prompts.

**IMPORTANT**: After installation, you MUST edit configuration:
```bash
nano ~/coyote_interactive/config_secrets.py
```

Add your API credentials (Azure OpenAI or Ollama endpoints).

## Manual Installation

If you prefer manual installation, follow the complete guide in [INSTALL.md](INSTALL.md).

## Quick Commands

### Start/Stop Service
```bash
# Start
systemctl --user start coyote.service

# Stop
systemctl --user stop coyote.service

# Restart
systemctl --user restart coyote.service

# Status
systemctl --user status coyote.service
```

### Attach to Running Session
```bash
# Using alias (added by install script)
b

# Or full command
byobu attach -t coyote_session

# Detach: Ctrl+B then D
```

### Run System Manager
```bash
cd ~/coyote_interactive/manager
./run_manager.py
```

### Manual Testing
```bash
cd ~/coyote_interactive
source venv/bin/activate
python coyote.py
```

## Verification Checklist

After installation, verify:

```bash
# Check whisper-stream is installed
whisper-stream --help

# Check environment variables
echo $PIPER_MODEL_COYOTE

# Check piper is installed
piper --help

# Check Python packages
source ~/coyote_interactive/venv/bin/activate
pip list | grep -E 'gpiozero|openai|textual'

# Check audio devices
arecord -l
pactl list sources short

# Check GPIO permissions
groups | grep gpio

# Check service status
systemctl --user status coyote.service
```

## Common Issues & Quick Fixes

### Service won't start
```bash
# Check logs
journalctl --user -u coyote.service -n 50

# Verify paths in service file
cat ~/.config/systemd/user/coyote.service

# Reload systemd after edits
systemctl --user daemon-reload
```

### Audio not working
```bash
# List audio devices
arecord -l
pactl list sources short

# Restart PulseAudio
pulseaudio -k && pulseaudio --start

# Test recording
arecord -D plughw:1,0 -f cd test.wav
```

### GPIO permissions
```bash
# Check groups
groups

# If gpio not listed, add user and reboot
sudo usermod -a -G gpio $USER
sudo reboot
```

### Python dependencies failed
```bash
# Install dev packages
sudo apt install python3-dev libdbus-1-dev libdbus-glib-1-dev

# Reinstall requirements
cd ~/coyote_interactive
source venv/bin/activate
pip install -r requirements.txt
```

### Voice synthesis fails (sox error)
```bash
# Install SOX (required for pitch shifting)
sudo apt install sox

# Verify environment variables
source /etc/environment
echo $PIPER_MODEL_COYOTE

# If still empty, set it manually for the test:
export PIPER_MODEL_COYOTE=/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx

# Test voice pipeline (pitch-shifted coyote)
# Note: If aplay fails with error 524, try a specific device like -D plughw:2,0
echo "Test" | piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | aplay -r 22050 -f S16_LE -t raw
```

## Hardware Setup

### GPIO Pin Assignments

From [config.py](config.py):

**Buttons:**
- GPIO 27: Intercom button (talk to person)
- GPIO 22: Plunger button (listen to television)

**LEDs:**
- GPIO 18: Dynamite LED
- GPIO 15: Intercom LED

**Switch:**
- GPIO 17: Wake/Sleep mode switch

### Audio Setup

**USB Microphones:**
- Microphone 0: Person/intercom input
- Microphone 1: Television audio input

Configure microphone numbers in `config.py` if different.

## Configuration Files

### Main Configuration
- [config.py](config.py) - Main settings (GPIO pins, file paths, prompts)
- `config_secrets.py` - API credentials (YOU MUST CREATE THIS)

### Important Settings

Edit `config.py` to customize:
- System messages (Wile E. Coyote personality)
- Whisper model paths
- Microphone numbers
- GPIO pin assignments
- LLM selection (Azure or Ollama)

## Project Structure

```
coyote_interactive/
├── coyote.py              # Main application
├── config.py              # Configuration
├── config_secrets.py      # API credentials (not in git)
├── install.sh             # Automated installation
├── INSTALL.md             # Detailed installation guide
├── README.md              # Project overview
├── requirements.txt       # Python dependencies
├── coyote.service         # Systemd service template
├── manager/               # System manager utility
│   ├── run_manager.py    # Start manager
│   └── check_system.py   # System configuration
├── audio_to_text/         # Whisper transcription
├── buttons/               # Button handling
├── leds/                  # LED control
└── sound_effects/         # Audio files
```

## First Time Setup Summary

1. **Run installer**
   ```bash
   cd ~/coyote_interactive
   ./install.sh
   ```

2. **Configure secrets**
   ```bash
   nano config_secrets.py
   ```

3. **Reboot** (for GPIO permissions)
   ```bash
   sudo reboot
   ```

4. **Start service**
   ```bash
   systemctl --user start coyote.service
   ```

5. **Verify**
   ```bash
   b  # Attach to session
   systemctl --user status coyote.service
   ```

## Getting Help

- Detailed installation: [INSTALL.md](INSTALL.md)
- Project overview: [README.md](README.md)
- System manager: [manager/README.md](manager/README.md)
- Service logs: `journalctl --user -u coyote.service`
- Attach to session: `b` or `byobu attach -t coyote_session`

## Default Credentials Template

When you create `config_secrets.py`, you need:

### For Azure OpenAI:
```python
AZURE_OPENAI_GPT4_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_GPT4_KEY = "your-api-key-here"
AZURE_MODEL = "gpt-4"  # or your deployment name
```

### For Ollama (local):
```python
OLLAMA_ENDPOINT = "http://localhost:11434"
OLLAMA_MODEL = "llama2"  # or your preferred model
```

Then set in `config.py`:
```python
LLM = "azure"  # or "ollama"
```
