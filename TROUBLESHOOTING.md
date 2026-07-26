# Troubleshooting Guide - Coyote Interactive

This guide covers common issues and their solutions when setting up and running Coyote Interactive on Raspberry Pi.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Service Won't Start](#service-wont-start)
3. [Audio Problems](#audio-problems)
4. [GPIO Issues](#gpio-issues)
5. [Python/Dependency Issues](#pythondependency-issues)
6. [Network Issues](#network-issues)
7. [LLM/API Issues](#llmapi-issues)
8. [Performance Issues](#performance-issues)

---

## Installation Issues

### Whisper.cpp Build Fails

**Symptom:** CMake or build errors during whisper.cpp compilation

**Solutions:**
```bash
# Install missing dependencies
sudo apt install -y cmake build-essential libsdl2-dev git wget

# Clean and rebuild
cd /opt/whisper.cpp
sudo rm -rf build
sudo cmake -B build -DWHISPER_SDL2=ON
sudo cmake --build build --config Release
```

If still failing on older Pis:
```bash
# Try without SDL2
sudo cmake -B build
sudo cmake --build build --config Release
```

### Piper Download Fails

**Symptom:** Cannot download piper or voice models

**Solutions:**
```bash
# Check architecture
uname -m

# For ARM64 (aarch64)
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz

# For ARM32 (armv7l)
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_armv7l.tar.gz

# If HuggingFace is slow, try alternative mirror or download separately
```

### Virtual Environment Creation Fails

**Symptom:** `python3 -m venv venv` fails

**Solutions:**
```bash
# Install python3-venv
sudo apt install python3-venv python3-pip

# Try removing old venv and recreating
rm -rf ~/coyote_interactive/venv
cd ~/coyote_interactive
python3 -m venv venv
```

---

### Whisper.cpp Issues

If `whisper-stream` fails:
- Check that SDL2 is installed: `dpkg -l | grep libsdl2`
- Verify model file exists: `ls -l /usr/share/whisper/models/`
- Test with: `whisper-stream -m /usr/share/whisper/models/ggml-base.en.bin --step 4500 --length 5000 -c 1 -t 2 -ac 512 --keep 85`
- If lagging on older Pis, try the tiny model: `whisper-stream -m /usr/share/whisper/models/ggml-tiny.en.bin --step 4500 --length 5000 -c 1 -t 2 -ac 512 --keep 85`

### Service Won't Start
**Symptom:** Coyote service fails to start or remains in "failed" state.

**Solutions:**
- Check logs: `journalctl --user -u coyote.service -n 50`
- Check byobu: `byobu list-sessions`
- Manually run: `cd ~/coyote_interactive && ./venv/bin/python coyote.py`

**Check if byobu session exists:**
```bash
byobu list-sessions
```

### Service File Path Issues

**Symptom:** Service fails with "No such file or directory"

**Solutions:**
```bash
# Verify service file exists
ls -l ~/.config/systemd/user/coyote.service

# Check paths in service file match your system
cat ~/.config/systemd/user/coyote.service

# Common issues:
# - Username not 'robot' - update all /home/robot/ paths
# - Virtual environment path wrong
# - Python script path wrong

# Edit service file
nano ~/.config/systemd/user/coyote.service

# After editing, reload systemd
systemctl --user daemon-reload
systemctl --user restart coyote.service
```

### Byobu Not Starting

**Symptom:** Service starts but no byobu session

**Solutions:**
```bash
# Install byobu
sudo apt install byobu

# Test byobu manually
byobu

# Exit: Ctrl+D

# Check if session already exists
byobu list-sessions

# Kill old session if stuck
byobu kill-session -t coyote_session

# Restart service
systemctl --user restart coyote.service
```

### Virtual Environment Not Activated

**Symptom:** Python module import errors in logs

**Solutions:**
```bash
# Verify venv exists
ls -l ~/coyote_interactive/venv/bin/activate

# Verify packages installed in venv
source ~/coyote_interactive/venv/bin/activate
pip list

# Reinstall if needed
pip install -r ~/coyote_interactive/requirements.txt
```

### Lingering Not Enabled

**Symptom:** Service only runs when user logged in

**Solutions:**
```bash
# Enable lingering
sudo loginctl enable-linger $USER

# Verify lingering enabled
loginctl show-user $USER | grep Linger

# Should show: Linger=yes
```

---

## Audio Problems

### Microphones Not Detected

**Symptom:** No microphones found or wrong device numbers

**Diagnose:**
```bash
# List all USB audio devices
lsusb | grep -i audio

# List ALSA recording devices
arecord -l

# List PulseAudio sources
pactl list sources short

# Check PulseAudio status
pactl info
```

**Solutions:**
```bash
# Restart PulseAudio
pulseaudio -k
pulseaudio --start

# If USB mics not showing, try unplugging and replugging

# Check dmesg for USB errors
dmesg | grep -i usb | tail -20

# Update microphone numbers in config.py
nano ~/coyote_interactive/config.py
# Update TRANSCRIBE_MIC_NUMBER and PERSON_MIC_NUMBER
```

### Audio Recording Fails

**Symptom:** arecord or whisper-stream fails to capture audio

**Test recording:**
```bash
# Test with ALSA (replace card/device numbers)
arecord -D plughw:1,0 -f cd -d 5 test.wav

# Play back
aplay test.wav

# Test with PulseAudio
parecord -d alsa_input.usb-0 test.wav

# If recording is silent, check levels
alsamixer
# Use F4 to switch to capture, arrow keys to adjust
```

**Solutions:**
```bash
# Set microphone as default
pactl set-default-source alsa_input.usb-YOUR_MIC_NAME

# Increase microphone volume
pactl set-source-volume @DEFAULT_SOURCE@ 80%

# Unmute if muted
pactl set-source-mute @DEFAULT_SOURCE@ 0
```

### Sound Effects Won't Play

**Symptom:** Startup sound or other effects don't play

**Solutions:**
```bash
# Test audio output
speaker-test -t wav -c 2

# Test specific sound file
aplay ~/coyote_interactive/sound_effects/meep-and-tongue.mp3

# If mp3 doesn't work with aplay, use mpg123
mpg123 ~/coyote_interactive/sound_effects/meep-and-tongue.mp3

# Install mpg123 if missing
sudo apt install mpg123

# Check volume
alsamixer
# F6 to select sound card, adjust with arrow keys
```

### SOX Not Installed

**Symptom:** `speak_text.py` fails with "sox: command not found"

**This is critical** - SOX is required for pitch shifting to create the coyote voice.

**Solutions:**
```bash
# Install SOX
sudo apt install sox

# Verify installation
sox --version

# Test the full voice pipeline
echo "Test" | piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | \
sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | \
aplay -r 22050 -f S16_LE -t raw
```

### Piper Environment Variable Not Set

**Symptom:** `speak_text.py` fails with "PIPER_MODEL_COYOTE: unbound variable" or no audio output

**Solutions:**
```bash
# Check if environment variable is set
echo $PIPER_MODEL_COYOTE

# If empty, add to /etc/environment
echo "PIPER_MODEL_COYOTE=/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx" | sudo tee -a /etc/environment

# Load it for current session
export PIPER_MODEL_COYOTE=/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx

# Verify
echo $PIPER_MODEL_COYOTE

# Note: Logout/login or reboot for system-wide effect
```

### Piper: Shared Library Not Found

**Symptom:** `piper: error while loading shared libraries: libpiper_phonemize.so.1: cannot open shared object file: No such file or directory`

This is common when using pre-built binaries on a fresh Pi.

**Solutions:**
```bash
# Locate your piper directory (where you downloaded/built it)
# Assuming it is in ~/coyote_interactive/piper

# Copy shared libraries to system library path
sudo cp ~/coyote_interactive/piper/lib* /usr/local/lib/

# Update the dynamic linker cache
sudo ldconfig

# Verify it works now
piper --version
```

### Piper: Model file or Model config doesn't exist

**Symptom:** `terminate called after throwing an instance of 'std::runtime_error' what(): Model file doesn't exist` (or `Model config doesn't exist`)

**Solutions:**
1. **Empty variable:** Ensure `$PIPER_MODEL_COYOTE` is set. Run `source /etc/environment`.
2. **Missing .json:** Piper requires both the `.onnx` file and a `.json` file with the same name.
   ```bash
   cd /usr/share/piper/voices/en_GB
   sudo wget -nc https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx.json
   ```

### Audio Error: Unknown error 524

**Symptom:** `aplay: main:850: audio open error: Unknown error 524` (or -524)

This usually means the default ALSA device (often HDMI or Headphone jack) is not supported or active.

**Solutions:**
1. **Change device:** Explicitly use your USB audio card.
2. **Check Card Numbers:** Run `aplay -l` to find your card number.
3. **Update Config:** Set `SPEAKER_DEVICE = "plughw:CARD_NUMBER,0"` in `config.py`.
   (e.g., `plughw:2,0` if your USB audio is Card 2).

### Audio Device Reassigned After Reboot (startup sound works, chat TTS silent)

**Symptom:**
- Startup `meep` sound plays, but spoken chat responses are silent.
- Logs may show configured speaker device failed, then fallback.

**Why this happens:**
- USB audio card indexes can change across reboots.
- `SPEAKER_DEVICE` in `config.py` can point to an old card index/device.

**Fast fix (2-3 minutes):**
```bash
cd ~/coyote_interactive

# 1) See current playback devices
aplay -l

# 2) Test likely USB outputs by speaking the device name through each device
MODEL=""
for c in "${PIPER_MODEL_COYOTE:-}" "${PIPER_MODEL:-}" \
   "/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx" \
   "/usr/share/piper/voices/en_GB/en_GB-alba-medium.onnx"; do
   if [[ -n "$c" && -f "$c" ]]; then MODEL="$c"; break; fi
done

for dev in "plughw:CARD=Audio,DEV=0" "plughw:CARD=Audio_1,DEV=0"; do
   echo "--- Testing $dev ---"
   printf "This is device %s. This is device %s.\n" "$dev" "$dev" | \
      piper --model "$MODEL" -s 71 --length_scale 1.4 --output-raw | \
      sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | \
      aplay -D "$dev" -r 22050 -f S16_LE -t raw
done

# 3) Set SPEAKER_DEVICE in config.py to the one you actually heard
# Example:
# SPEAKER_DEVICE = "plughw:CARD=Audio_1,DEV=0"

# 4) Restart service
systemctl --user restart coyote.service
```

**Tip:** Prefer named devices (`CARD=Audio` / `CARD=Audio_1`) over numeric `plughw:2,0` style indexes. Named devices are usually more stable.

### Piper TTS No Output

**Symptom:** Text-to-speech generates no audio

**Test:**
```bash
# Test piper directly
echo "Hello from Wile E. Coyote" | piper \
  --model /usr/share/piper/voices/en_GB/en_GB-alba-medium.onnx \
  --output_file test_tts.wav

# Play the result
aplay test_tts.wav

# If fails, verify model exists
ls -l /usr/share/piper/voices/en_GB/

# Test with the actual coyote voice pipeline
echo "Test" | piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | \
sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | \
aplay -r 22050 -f S16_LE -t raw
```

---

## GPIO Issues

### GPIO Permission Denied

**Symptom:** "Permission denied" when accessing GPIO pins

**Solutions:**
```bash
# Check user is in gpio group
groups

# If gpio not listed, add user
sudo usermod -a -G gpio $USER

# Log out and log back in (or reboot)
sudo reboot

# Verify after reboot
groups | grep gpio
```

### gpiozero Import Error

**Symptom:** `ModuleNotFoundError: No module named 'gpiozero'`

**Solutions:**
```bash
cd ~/coyote_interactive
source venv/bin/activate

# Install gpiozero and lgpio
pip install gpiozero lgpio

# Verify installation
python -c "import gpiozero; print(gpiozero.__version__)"
```

### Buttons Don't Respond

**Symptom:** Button presses not detected

**Test:**
```bash
# Test GPIO pins with simple script
python3 << 'EOF'
from gpiozero import Button
from signal import pause

def button_pressed():
    print("Button 27 pressed!")

button = Button(27)  # Test GPIO 27
button.when_pressed = button_pressed

print("Press button on GPIO 27...")
pause()
EOF
```

**Check:**
- Verify GPIO pin numbers in `config.py` match physical connections
- Check button wiring (pull-up/pull-down configuration)
- Test with multimeter/oscilloscope if available

### LEDs Don't Light Up

**Symptom:** LEDs don't respond to GPIO output

**Test:**
```bash
# Test LED control
python3 << 'EOF'
from gpiozero import LED
from time import sleep

led = LED(18)  # Test GPIO 18
print("Blinking LED on GPIO 18...")
for i in range(5):
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
print("Done")
EOF
```

**Check:**
- Verify LED wiring (anode/cathode, resistor)
- Check GPIO pin numbers in `config.py`
- Test with different GPIO pin to rule out hardware failure

---

## Python/Dependency Issues

### dbus-python Install Fails

**Symptom:** `pip install dbus-python` fails to compile

**Solutions:**
```bash
# Install development dependencies
sudo apt install libdbus-1-dev libdbus-glib-1-dev python3-dev

# Reinstall
source ~/coyote_interactive/venv/bin/activate
pip install dbus-python
```

### python-networkmanager Fails

**Symptom:** NetworkManager Python bindings fail

**Solutions:**
```bash
# Install system package first
sudo apt install python3-networkmanager

# Then install in venv
source ~/coyote_interactive/venv/bin/activate
pip install python-networkmanager
```

### ImportError for System Packages

**Symptom:** Cannot import system-installed Python packages in venv

**Solutions:**
```bash
# Create venv with system packages
rm -rf ~/coyote_interactive/venv
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Network Issues

### WiFi Manager Not Working

**Symptom:** Cannot connect to WiFi via system manager

**Solutions:**
```bash
# Check NetworkManager is running
systemctl status NetworkManager

# Start if not running
sudo systemctl start NetworkManager

# Enable for auto-start
sudo systemctl enable NetworkManager

# Check sudo permissions (needed for WiFi control)
sudo -l | grep nmcli

# Run check_system.py to configure
cd ~/coyote_interactive/manager
python check_system.py
```

### VPN Connection Fails

**Symptom:** VPN won't connect via manager

**Check:**
```bash
# Verify VPN configuration exists
nmcli connection show

# Test VPN manually
nmcli connection up <vpn-name>

# Check logs
journalctl -u NetworkManager -n 50
```

---

## LLM/API Issues

### OpenAI API Errors

**Symptom:** "Authentication failed" or connection errors

**Solutions:**
```bash
# Verify config_secrets.py exists and has correct values
cat ~/coyote_interactive/config_secrets.py

# Test Azure OpenAI connection
python3 << 'EOF'
import os
os.chdir('/home/YOUR_USER/coyote_interactive')  # Update path
from config_secrets import AZURE_OPENAI_GPT4_ENDPOINT, AZURE_OPENAI_GPT4_KEY
print(f"Endpoint: {AZURE_OPENAI_GPT4_ENDPOINT}")
print(f"Key: {AZURE_OPENAI_GPT4_KEY[:10]}...")
EOF

# Verify LLM setting in config.py
grep "^LLM" ~/coyote_interactive/config.py
```

### Ollama Connection Fails

**Symptom:** Cannot connect to Ollama

**Solutions:**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Test with specific model
ollama run llama2 "test"

# Update OLLAMA_ENDPOINT in config_secrets.py if using remote server
```

### AX650 Runtime or Generation Fails

**Symptom:** `LLM = "ax650"` responses fail, or startup/BOOM reset logs errors

**Notes:**
- AX650 generation uses `:11434` and sends only the latest user prompt (not full message history).
- AX650 runtime reset uses `:8000` in this order: stop, then reset with `system_prompt`.

**Checks:**
```bash
# Verify provider mode
grep "^LLM" ~/coyote_interactive/config.py

# Verify AX650 config values
grep "^AX650_" ~/coyote_interactive/config_secrets.py

# Check generation service
curl http://localhost:11434/api/tags

# Test generation call shape expected by coyote
curl -X POST http://localhost:11434/api/generate \
   -H "Content-Type: application/json" \
   -d '{"model":"qwen3-ax650","prompt":"hello","stream":false}'

# Check runtime stop/reset endpoints
curl http://127.0.0.1:8000/api/stop
curl -X POST http://127.0.0.1:8000/api/reset \
   -H "Content-Type: application/json" \
   -d '{"system_prompt":"test prompt"}'
```

If `:11434` works but `:8000` fails, conversations may still be logged locally but startup/BOOM runtime reset behavior will not complete.

### Model Not Found

**Symptom:** "Model not found" errors

**Check configuration:**
```python
# In config_secrets.py:
# For Azure: AZURE_MODEL should match your deployment name, not "gpt-4"
# For Ollama: OLLAMA_MODEL should match installed model
# For AX650: AX650_MODEL should match the local AX650-served model name

# List available Ollama models
ollama list
```

---

## Performance Issues

### High CPU Usage

**Symptom:** System slow, high temperature

**Solutions:**
```bash
# Check CPU usage
top

# Use lighter Whisper model
# Edit config.py to use tiny.en instead of base.en
nano ~/coyote_interactive/config.py

# Download tiny model if needed
cd /opt/whisper.cpp
sudo sh ./models/download-ggml-model.sh tiny.en
sudo mv models/ggml-tiny.en.bin /usr/share/whisper/models/

# Reduce transcription threads
# Edit config.py: TRANSCRIBE_THREADS = "1"
```

### Slow Response Time

**Symptom:** System responds slowly to button presses

**Check:**
```bash
# Monitor system resources
htop

# Check for swapping
free -h

# If low memory:
# - Close unnecessary applications
# - Use lighter models (tiny.en for Whisper)
# - Reduce LLM token limits in config_secrets.py
```

### Transcription Lag

**Symptom:** Audio transcription is slow or delayed

**Solutions:**
```bash
# Use smaller Whisper model (tiny.en instead of base.en)
# Reduce thread count if overheating
# Ensure SD card is fast (Class 10 or better)
# Consider USB 3.0 SSD boot for better I/O
```

---

## Advanced Troubleshooting

### Enable Debug Logging

Add to your Python scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitor System Logs

```bash
# Watch all system logs
sudo journalctl -f

# Watch service logs
journalctl --user -f -u coyote.service

# System messages
dmesg -w
```

### Check System Resources

```bash
# CPU temperature
vcgencmd measure_temp

# Memory usage
free -h

# Disk space
df -h

# Process tree
pstree -p
```

### Test Components Individually

```bash
# Test just audio transcription
cd ~/coyote_interactive/audio_to_text
python transcribe_continuously.py \
  --whisper_model /usr/share/whisper/models/ggml-base.en.bin

# Test just LED control
python -c "from leds.led_manager import LEDManager; import time; lm = LEDManager(); lm.start(); time.sleep(5); lm.stop()"

# Test just button handling
python -c "from buttons.button_manager import ButtonManager; import signal; bm = ButtonManager(); signal.pause()"
```

---

## Getting More Help

If issues persist:

1. **Check logs thoroughly:**
   ```bash
   journalctl --user -u coyote.service -n 200 > ~/coyote_debug.log
   ```

2. **Attach to session and observe:**
   ```bash
   b  # Watch for error messages
   ```

3. **Run manual test with full output:**
   ```bash
   cd ~/coyote_interactive
   source venv/bin/activate
   python -u coyote.py 2>&1 | tee ~/coyote_output.log
   ```

4. **Document your issue:**
   - What were you trying to do?
   - What happened instead?
   - What error messages appeared?
   - What have you tried?
   - Include relevant log excerpts

5. **Review documentation:**
   - [INSTALL.md](INSTALL.md)
   - [README.md](README.md)
   - [QUICKSTART.md](QUICKSTART.md)
   - Component-specific READMEs in subdirectories

6. **Check hardware:**
   - Verify all connections are secure
   - Test components individually
   - Check power supply is adequate (5V 3A minimum for Pi 4)
