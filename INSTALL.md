# Coyote Interactive - Complete Raspberry Pi Installation Guide

This guide will walk you through installing everything needed for the Coyote Interactive project on a fresh Raspberry Pi.

## Prerequisites

- Raspberry Pi (tested on Pi 4/5) running Raspberry Pi OS (64-bit recommended)
- Hardware components connected (GPIO buttons, LEDs, switches, USB microphones)
- Internet connection
- User account (this guide assumes username `robot`, adjust paths as needed)

## Installation Steps

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install System Dependencies

```bash
sudo apt install -y \
    python3 python3-pip python3-venv \
    git cmake build-essential wget \
    libsdl2-dev \
    pulseaudio pavucontrol \
    network-manager \
    byobu \
    alsa-utils \
    espeak-ng \
    libgpiod2 python3-libgpiod \
    dbus libdbus-1-dev libdbus-glib-1-dev \
    python3-dev pkg-config \
    ffmpeg \
    mpg123 \
    sox
```

**Important packages explained:**
- `sox` - Sound eXchange, required for audio pitch shifting (creates the coyote voice character)
- `espeak-ng` - Text-to-speech engine used by Piper
- `pulseaudio` - Audio routing and management
- `libgpiod2` - GPIO control library for buttons/LEDs

### 3. Install Whisper.cpp (Audio Transcription)

Install `whisper.cpp` for real-time audio transcription:

```bash
# Clone whisper.cpp repository
sudo git clone https://github.com/ggerganov/whisper.cpp /opt/whisper.cpp
cd /opt/whisper.cpp

# Create models directory
sudo mkdir -p /usr/share/whisper/models

# Download the base English model (recommended for quality)
sudo sh ./models/download-ggml-model.sh base.en
sudo mv models/ggml-base.en.bin /usr/share/whisper/models/

# Download the tiny English model (faster performance for older Pis)
sudo sh ./models/download-ggml-model.sh tiny.en
sudo mv models/ggml-tiny.en.bin /usr/share/whisper/models/

# Build whisper.cpp with SDL2 support
sudo cmake -B build -DWHISPER_SDL2=ON
sudo cmake --build build --config Release

# Install binaries
sudo cp build/bin/* /usr/local/bin/
sudo chmod +x /usr/local/bin/*

# Verify installation
whisper-stream --help
```

### 4. Install Piper TTS (Text-to-Speech)

#### Option A: Install Pre-built Piper Binary (Recommended - Faster)

Install Piper for voice synthesis:

```bash
# Create piper directory
sudo mkdir -p /usr/share/piper/voices

# Download Piper executable (adjust for your Pi architecture)
# For ARM64 (Pi 4/5 with 64-bit OS):
cd /tmp
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz
tar -xzf piper_linux_aarch64.tar.gz
sudo cp piper/piper /usr/local/bin/
sudo chmod +x /usr/local/bin/piper

# Copy shared libraries and update loader cache
sudo cp piper/lib* /usr/local/lib/
sudo ldconfig

# Download voice models
cd /usr/share/piper/voices

# Download British English voice (alba-medium)
sudo mkdir -p en_GB
cd en_GB
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json

# Download VCTK voice for coyote (multi-speaker model)
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx.json

# Verify installation
piper --help
```

**Note**: For ARM32 (32-bit OS), use `piper_linux_armv7l.tar.gz` instead. The `--inet4-only` flag helps avoid IPv6 issues on some Raspberry Pi configurations.

#### Option B: Build Piper from Source (Alternative - More Reliable)

If the pre-built binary doesn't work on your system, build from source:

```bash
# Install additional build dependencies (espeak-ng already installed in step 2)
sudo apt install -y build-essential cmake git

# Clone and build Piper
sudo mkdir -p /opt/piper
sudo git clone --recursive https://github.com/rhasspy/piper /opt/piper
cd /opt/piper

# Build (this takes 15-30 minutes)
sudo mkdir -p build
cd build
sudo cmake ..
sudo make -j$(nproc)

# Install binaries
sudo cp piper /usr/local/bin/
sudo chmod +x /usr/local/bin/piper
sudo cp libpiper_phonemize.so /usr/local/lib/
sudo ldconfig

# Download voice models (same as Option A)
sudo mkdir -p /usr/share/piper/voices/en_GB
cd /usr/share/piper/voices/en_GB
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx
sudo wget --inet4-only https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx.json

# Verify
piper --help
```

### 5. Setup Environment Variables

Configure environment variables for Piper and Whisper models:

```bash
# Add model paths to system environment
echo "PIPER_MODEL=/usr/share/piper/voices/en_GB/en_GB-alba-medium.onnx" | sudo tee -a /etc/environment
echo "PIPER_MODEL_COYOTE=/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx" | sudo tee -a /etc/environment

# Load the new environment variables (or logout/login)
source /etc/environment

# Verify (these should print the paths)
echo $PIPER_MODEL_COYOTE
```

**Note**: These environment variables are used by:
- `speak_text.py` - Uses `$PIPER_MODEL_COYOTE` for the coyote voice
- They persist across reboots and all user sessions

### 6. Clone and Setup Project

```bash
# Navigate to home directory
cd ~

# Clone the project (if not already done)
# git clone <repository_url> coyote_interactive

# Navigate to project directory
cd ~/coyote_interactive

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install manager package (optional but recommended)
pip install -e ./manager
```

### 7. Configure Secrets and Settings

```bash
# Create config_secrets.py from template
cp config_secrets.example.py config_secrets.py

# Edit the secrets file with your actual credentials
nano config_secrets.py
```

**Required Configuration:**
- If using Azure OpenAI: Set `AZURE_OPENAI_GPT4_ENDPOINT`, `AZURE_OPENAI_GPT4_KEY`, and `AZURE_MODEL`
- If using Ollama: Set `OLLAMA_ENDPOINT` and `OLLAMA_MODEL`
- Update `LLM` variable in `config.py` to either `"azure"` or `"ollama"`

### 8. Verify Audio Setup

```bash
# List audio input devices
arecord -l

# List PulseAudio sources
pactl list sources short

# Test microphone recording (Ctrl+C to stop)
arecord -D plughw:1,0 -f cd test.wav

# Play back the recording
aplay test.wav

# Adjust microphone volume if needed
alsamixer
```

### 9. Configure GPIO Permissions

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# You may need to log out and back in for group changes to take effect
```

### 10. Create Required Directories

```bash
cd ~/coyote_interactive

# Create conversation data directory
mkdir -p conversation_data

# Create audio transcription directory if needed
mkdir -p audio_to_text
```

### 11. Run System Configuration Check

```bash
cd ~/coyote_interactive/manager
python check_system.py
```

This script will:
- Check and configure sudo permissions for NetworkManager
- Verify systemd configuration
- Enable user lingering for autostart
- Check system dependencies

Answer 'y' when prompted to configure settings.

### 12. Setup Systemd Service for Auto-start

```bash
# Create systemd user directory
mkdir -p ~/.config/systemd/user/

# Copy service file and update paths
cp ~/coyote_interactive/coyote.service ~/.config/systemd/user/

# Edit service file to match your username and paths
nano ~/.config/systemd/user/coyote.service
```

**Important**: Update the following in `coyote.service`:
- Replace `/home/robot/` with your actual home path (e.g., `/home/pi/`)
- Verify all path references are correct

```bash
# Reload systemd daemon
systemctl --user daemon-reload

# Enable service for auto-start on boot
systemctl --user enable coyote.service

# Enable lingering (allows service to run without user login)
sudo loginctl enable-linger $USER

# Add convenient alias to attach to byobu session
echo "alias b='byobu attach -t coyote_session'" >> ~/.bashrc
source ~/.bashrc
```

### 13. Voice Customization (Optional)

The coyote voice is created using a pipeline of Piper TTS + SOX audio processing. Understanding these parameters helps you customize the character voice:

#### Voice Pipeline Explained

From `speak_text.py`, the voice generation command:
```bash
piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | \
sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | \
aplay -r 22050 -f S16_LE -t raw
```

#### Parameters:

**Piper Parameters:**
- `--model $PIPER_MODEL_COYOTE` - Uses the VCTK multi-speaker model
- `-s 71` - Speaker selection (VCTK has 109 speakers, speaker 71 chosen for character)
- `--length_scale 1.75` - Speech speed (1.75 = 75% slower, more deliberate)
- `--output-raw` - Outputs raw PCM audio for SOX processing

**SOX Parameters:**
- `pitch -200` - Lowers pitch by 200 cents (2 semitones) for deeper, coyote-like voice
- `vol 0.98` - Slight volume reduction to prevent clipping
- Audio format: `22050 Hz, signed 16-bit, mono`

#### Customization Options:

To experiment with different voices, edit `speak_text.py`:

```python
# Try different speakers (0-108 for VCTK model)
-s 71    # Current: Male voice
-s 10    # Example: Different male voice
-s 5     # Example: Female voice

# Adjust speech speed
--length_scale 1.75   # Current: Slower, deliberate
--length_scale 1.0    # Normal speed
--length_scale 2.0    # Even slower

# Adjust pitch shift
pitch -200   # Current: Deeper voice
pitch -300   # Even deeper
pitch -100   # Slightly deeper
pitch 0      # No pitch change
```

**Test your changes:**
```bash
echo "Hello, I am Wile E. Coyote!" | \
piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | \
sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | \
aplay -r 22050 -f S16_LE -t raw
```

### 14. Test Installation

Before starting the service, test manually:

```bash
cd ~/coyote_interactive
source venv/bin/activate
python coyote.py
```

Press Ctrl+C to stop after verifying it starts without errors.

### 15. Start the Service

```bash
# Start the service
systemctl --user start coyote.service

# Check service status
systemctl --user status coyote.service

# Attach to the running session
byobu attach -t coyote_session
# Or use the alias:
b

# Detach from byobu session: Ctrl+B, then D
```

### 16. Test System Manager

```bash
cd ~/coyote_interactive/manager
./run_manager.py
```

Use the manager to:
- Configure WiFi networks
- Adjust audio volume
- Monitor service status
- View transcripts

## Verification Checklist

- [ ] Whisper.cpp installed and `whisper-stream` command available
- [ ] Piper TTS installed and voice models downloaded
- [ ] Python virtual environment created and activated
- [ ] All Python dependencies installed without errors
- [ ] `config_secrets.py` configured with API credentials
- [ ] Audio devices detected and working
- [ ] GPIO permissions configured
- [ ] System config check completed successfully
- [ ] Systemd service installed and enabled
- [ ] Coyote service starts without errors
- [ ] System manager runs successfully

## Troubleshooting

### Whisper.cpp Issues

If `whisper-stream` fails:
- Check that SDL2 is installed: `dpkg -l | grep libsdl2`
- Verify model file exists: `ls -l /usr/share/whisper/models/`
- Test with: `whisper-stream -m /usr/share/whisper/models/ggml-base.en.bin -t 2`

### Piper TTS Issues

If Piper fails:
- Check architecture: `uname -m` (should be aarch64 for ARM64)
- Verify voice models: `ls -l /usr/share/piper/voices/en_GB/`
- Test with: `echo "test" | piper --model /usr/share/piper/voices/en_GB/en_GB-alba-medium.onnx --output_file test.wav`

### GPIO Issues

If GPIO doesn't work:
- Verify user is in gpio group: `groups`
- Check GPIO chip: `gpioinfo`
- Install lgpio: `pip install lgpio`

### Service Won't Start

If systemd service fails:
- Check logs: `journalctl --user -u coyote.service -n 50`
- Verify paths in service file match your system
- Ensure virtual environment exists
- Check byobu is installed: `which byobu`

### Audio Issues

If microphones not detected:
- List USB devices: `lsusb`
- Check PulseAudio: `pactl info`
- Restart PulseAudio: `pulseaudio -k && pulseaudio --start`

### Python Dependency Issues

If pip install fails:
- Install development headers: `sudo apt install python3-dev`
- For dbus-python: `sudo apt install libdbus-1-dev`
- For NetworkManager: `sudo apt install libdbus-glib-1-dev`

## Post-Installation

After successful installation:

1. **Configure Network**: Use the system manager to set up WiFi credentials
2. **Test Features**: 
   - Press buttons to verify GPIO works
   - Test audio transcription
   - Check LED functionality
   - Verify sound effects play
3. **Monitor Service**: Use `systemctl --user status coyote.service` regularly
4. **Check Logs**: Attach to byobu session to see live output

## Next Steps

- Read the main [README.md](README.md) for usage instructions
- Review [manager/README.md](manager/README.md) for system manager details
- Customize system messages in `config.py` as desired
- Add your conversation archives to version control if needed

## Support

If you encounter issues not covered here:
1. Check service logs: `journalctl --user -u coyote.service`
2. Attach to session: `byobu attach -t coyote_session`
3. Run manager: `./manager/run_manager.py` to check system status
4. Verify all paths match your username and installation location
