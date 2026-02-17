# 🎯 Welcome to Coyote Interactive Setup

This document helps you navigate all the installation resources for setting up Coyote Interactive on your Raspberry Pi.

## 📚 Installation Resources Overview

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Quick reference and commands | When you need a quick reminder or command lookup |
| **[install.sh](install.sh)** | Automated installation script | For first-time installation (recommended) |
| **[INSTALL.md](INSTALL.md)** | Complete step-by-step guide | For manual installation or understanding details |
| **[INSTALLATION_CHECKLIST.md](INSTALLATION_CHECKLIST.md)** | Printable checklist | To track progress during installation |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Problem-solving guide | When something doesn't work |
| **[README.md](README.md)** | Project overview and usage | To understand what the project does |

---

## 🚀 Quick Start (Recommended Path)

### For Brand New Setup:

1. **Start with automated installation:**
   ```bash
   cd ~/coyote_interactive
   ./install.sh
   ```

2. **Follow the prompts** - the script will install everything

3. **Configure your API credentials:**
   ```bash
   nano ~/coyote_interactive/config_secrets.py
   ```

4. **Reboot** (for GPIO permissions):
   ```bash
   sudo reboot
   ```

5. **Start the service:**
   ```bash
   systemctl --user start coyote.service
   ```

6. **Verify it's running:**
   ```bash
   b  # Attach to session
   ```

**That's it!** Your coyote should now be interactive.

---

## 📖 Detailed Path (Manual Installation)

### If you prefer step-by-step control:

1. **Read [INSTALL.md](INSTALL.md)** - comprehensive installation guide

2. **Print [INSTALLATION_CHECKLIST.md](INSTALLATION_CHECKLIST.md)** - track your progress

3. **Follow each step manually** - gives you full understanding

4. **Refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** if issues arise

---

## 🔍 What's Installed?

The installation sets up:

### System Components
- ✅ **Whisper.cpp** - Real-time audio transcription
- ✅ **Piper TTS** - Voice synthesis
- ✅ **SOX** - Audio processing for pitch shifting (creates coyote voice)
- ✅ **Python 3** - Runtime environment
- ✅ **Byobu** - Terminal session manager
- ✅ **PulseAudio** - Audio management
- ✅ **NetworkManager** - Network control
- ✅ **GPIO libraries** - Hardware interface

### Python Dependencies
- ✅ **gpiozero** - GPIO control
- ✅ **openai** - LLM API client
- ✅ **textual** - Terminal UI framework
- ✅ **pulsectl** - Audio control
- ✅ **python-networkmanager** - Network control
- ✅ And more... (see requirements.txt)

### Project Components
- ✅ **Main application** (coyote.py)
- ✅ **System manager** (manager/)
- ✅ **Audio transcription** (audio_to_text/)
- ✅ **LED control** (leds/)
- ✅ **Button handling** (buttons/)
- ✅ **Sound effects** (sound_effects/)

---

## ⚙️ Configuration Required

After installation, you **MUST** configure:

### 1. API Credentials (Required)
Edit `config_secrets.py` with your LLM API credentials:

**For Azure OpenAI:**
```python
AZURE_OPENAI_GPT4_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_GPT4_KEY = "your-api-key-here"
AZURE_MODEL = "gpt-4"  # your deployment name
```

**For Ollama (local):**
```python
OLLAMA_ENDPOINT = "http://localhost:11434"
OLLAMA_MODEL = "llama2"
```

Then set in `config.py`:
```python
LLM = "azure"  # or "ollama"
```

### 2. GPIO Pin Verification (If hardware differs)
Check `config.py` GPIO assignments match your wiring:
- Buttons: GPIO 27, 22
- LEDs: GPIO 18, 15  
- Switch: GPIO 17

### 3. Microphone Numbers (If needed)
Verify microphone device numbers with:
```bash
arecord -l
```
Update in `config.py` if different:
```python
TRANSCRIBE_MIC_NUMBER = "1"
PERSON_MIC_NUMBER = "0"
```

---

## 🧪 Testing Your Installation

### Quick Tests:

```bash
# Test whisper is installed
whisper-stream --help

# Test piper is installed
piper --help
# If fails with missing libpiper_phonemize:
# sudo cp ~/coyote_interactive/piper/lib* /usr/local/lib/ && sudo ldconfig

# Test SOX is installed (CRITICAL)
sox --version

# Test environment variables are set
echo $PIPER_MODEL_COYOTE

# Test Python environment
cd ~/coyote_interactive
source venv/bin/activate
python -c "import gpiozero, openai, textual; print('OK')"

# Test audio recording
arecord -l

# Test complete voice pipeline
echo "I am Wile E. Coyote" | piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | aplay -r 22050 -f S16_LE -t raw

# Test service status
systemctl --user status coyote.service

# Attach to running session
b
```

### Full System Test:

1. **Run System Manager:**
   ```bash
   cd ~/coyote_interactive/manager
   ./run_manager.py
   ```

2. **Check each component:**
   - Network status
   - Audio devices
   - Service status

3. **Test hardware:**
   - Press buttons
   - Verify LEDs light up
   - Speak into microphones
   - Listen for responses

---

## 🆘 Getting Help

### If Something Doesn't Work:

1. **Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** first
   - Covers 90% of common issues
   - Organized by problem type
   - Includes solutions and commands

2. **View service logs:**
   ```bash
   journalctl --user -u coyote.service -n 50
   ```

3. **Attach to session and watch output:**
   ```bash
   b  # Look for error messages
   ```

4. **Run manual test:**
   ```bash
   cd ~/coyote_interactive
   source venv/bin/activate
   python coyote.py
   ```

5. **Review installation checklist:**
   - Did you complete all steps?
   - Any warnings during installation?
   - All dependencies installed?

---

## 📋 Quick Command Reference

```bash
# Service control
systemctl --user start coyote.service    # Start
systemctl --user stop coyote.service     # Stop
systemctl --user restart coyote.service  # Restart
systemctl --user status coyote.service   # Status

# Session management
b                                         # Attach to session
# Ctrl+B then D                          # Detach from session

# Logs
journalctl --user -u coyote.service -n 50  # View logs

# Manual run
cd ~/coyote_interactive
source venv/bin/activate
python coyote.py

# System manager
cd ~/coyote_interactive/manager
./run_manager.py
```

---

## 📖 Additional Reading

- **[README.md](README.md)** - Project overview, features, and usage
- **[manager/README.md](manager/README.md)** - System manager details
- **[audio_to_text/README.md](audio_to_text/README.md)** - Transcription setup

---

## ✅ Success Checklist

You're done when:
- [ ] Installation completed without errors
- [ ] **SOX installed**: `sox --version` works
- [ ] **Environment variables set**: `echo $PIPER_MODEL_COYOTE` shows path
- [ ] API credentials configured in config_secrets.py
- [ ] Service starts: `systemctl --user status coyote.service`
- [ ] Can attach to session: `b`
- [ ] **Voice pipeline works**: Test command produces pitch-shifted coyote voice
- [ ] Buttons respond to presses
- [ ] LEDs light up correctly
- [ ] Audio transcription works
- [ ] **Character Voice Check:** Verify voice has the -200 pitch shift (Coyote character)
- [ ] LLM generates responses
- [ ] No errors in logs

---

## 🎉 You're Ready!

Once everything is working:

1. **Read the [README.md](README.md)** to understand operation modes
2. **Experiment with button presses** and features
3. **Configure WiFi** via system manager if needed
4. **Customize system messages** in config.py if desired
5. **Enjoy your interactive Wile E. Coyote!**

---

## 💡 Tips

- Use `b` alias to quickly attach to the session
- System manager is great for troubleshooting
- Service auto-starts on boot (no manual intervention needed)
- Conversation data is saved in `conversation_data/`
- Press both buttons in sleep mode to archive conversations (BOOM!)

---

**Need help?** Start with [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 🔧

**Questions about features?** See [README.md](README.md) 📖

**Installation issues?** Check [INSTALL.md](INSTALL.md) 📚
