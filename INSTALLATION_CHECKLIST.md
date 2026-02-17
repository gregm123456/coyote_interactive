# Coyote Interactive - Installation Checklist

Print this checklist and check off each step as you complete the installation.

## Pre-Installation
- [ ] Raspberry Pi with Raspberry Pi OS installed
- [ ] Internet connection configured
- [ ] Hardware connected (buttons, LEDs, switches, USB microphones)
- [ ] Project code downloaded/cloned to `~/coyote_interactive`

## Automated Installation

- [ ] Run: `cd ~/coyote_interactive`
- [ ] Run: `./install.sh`
- [ ] Follow all prompts in the installer
- [ ] Installer completed without errors

## Configuration

- [ ] Edit `config_secrets.py`: `nano ~/coyote_interactive/config_secrets.py`
- [ ] Add Azure OpenAI or Ollama credentials
- [ ] Set `LLM` variable in `config.py` to `"azure"` or `"ollama"`
- [ ] Verify GPIO pin assignments in `config.py` match your hardware
- [ ] Verify microphone numbers in `config.py` (test with `arecord -l`)

## Post-Installation

- [ ] Log out and log back in (for GPIO group permissions)
- [ ] Run system config check: `cd ~/coyote_interactive/manager && python check_system.py`
- [ ] Answer 'y' to configure system settings

## Testing

### Manual Test
- [ ] Run: `cd ~/coyote_interactive`
- [ ] Run: `source venv/bin/activate`
- [ ] Run: `python coyote.py`
- [ ] Verify it starts without errors
- [ ] Press Ctrl+C to stop
- [ ] Test buttons work (if ready)
- [ ] Test LEDs light up (if ready)
- [ ] Test audio transcription (if ready)

### Audio Verification
- [ ] List devices: `arecord -l`
- [ ] Note microphone card/device numbers
- [ ] Update `config.py` if mic numbers differ
- [ ] Test recording: `arecord -D plughw:1,0 -f cd test.wav`
- [ ] Test playback: `aplay test.wav`
- [ ] Adjust volume if needed: `alsamixer`

### Whisper Test
- [ ] Run: `whisper-stream --help`
- [ ] Verify model: `ls -l /usr/share/whisper/models/ggml-base.en.bin`
- [ ] Test transcription with microphone

### Piper Test
- [ ] Run: `piper --help`
- [ ] **Library Check:** If `piper --help` fails with "libpiper_phonemize.so.1" missing: `sudo cp ~/coyote_interactive/piper/lib* /usr/local/lib/ && sudo ldconfig`
- [ ] Verify models: `ls -l /usr/share/piper/voices/en_GB/`
- [ ] Test TTS: `echo "test" | piper --model /usr/share/piper/voices/en_GB/en_GB-alba-medium.onnx --output_file test.wav && aplay test.wav`

### SOX Test
- [ ] Run: `sox --version`
- [ ] Verify SOX installed: `which sox`

### Environment Variables
- [ ] Check: `echo $PIPER_MODEL_COYOTE`
- [ ] Should output: `/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx`
- [ ] If empty, add to `/etc/environment` and logout/login

### System Manager Test
- [ ] Run: `cd ~/coyote_interactive/manager`
- [ ] Run: `./run_manager.py`
- [ ] Navigate through menus
- [ ] Check network status
- [ ] Check audio devices
- [ ] Exit manager

## Service Setup

- [ ] Service file created: `ls ~/.config/systemd/user/coyote.service`
- [ ] Verify paths in service file match your username
- [ ] Reload systemd: `systemctl --user daemon-reload`
- [ ] Enable service: `systemctl --user enable coyote.service`
- [ ] Enable lingering: `sudo loginctl enable-linger $USER`
- [ ] Start service: `systemctl --user start coyote.service`
- [ ] Check status: `systemctl --user status coyote.service`
- [ ] Service shows as "active (running)"

### Service Verification
- [ ] Attach to session: `b` or `byobu attach -t coyote_session`
- [ ] Verify coyote.py is running in byobu
- [ ] No error messages in output
- [ ] Detach from session: Ctrl+B then D
- [ ] Service continues running after detach

## Final Verification

- [ ] Reboot system: `sudo reboot`
- [ ] After reboot, check service auto-started: `systemctl --user status coyote.service`
- [ ] Service is running without manual start
- [ ] Attach to session: `b`
- [ ] System responds to button presses
- [ ] LEDs function correctly
- [ ] Audio transcription works
- [ ] Text-to-speech works
- [ ] Conversation logging works

## Troubleshooting (if needed)

If issues occur, check:

- [ ] Service logs: `journalctl --user -u coyote.service -n 50`
- [ ] Check for errors in byobu session: `b`
- [ ] Verify API credentials in `config_secrets.py`
- [ ] Test microphones: `arecord -l` and `pactl list sources`
- [ ] Check GPIO permissions: `groups | grep gpio`
- [ ] Verify Python packages: `source venv/bin/activate && pip list`
- [ ] Check whisper: `which whisper-stream`
- [ ] Check piper: `which piper`
- [ ] Review INSTALL.md troubleshooting section

## Documentation Review

- [ ] Read [README.md](README.md) for usage instructions
- [ ] Read [INSTALL.md](INSTALL.md) for detailed installation info
- [ ] Read [QUICKSTART.md](QUICKSTART.md) for quick reference
- [ ] Read [manager/README.md](manager/README.md) for system manager details
- [ ] Bookmark service commands for future reference

## Optional Enhancements

- [ ] Configure WiFi networks via system manager
- [ ] Set up VPN if needed
- [ ] Adjust audio volumes to optimal levels
- [ ] Customize system messages in `config.py`
- [ ] Test conversation archiving (press both buttons in sleep mode)
- [ ] Set up automatic backups of conversation data
- [ ] Add custom sound effects
- [ ] Customize LED patterns

## Success Criteria

Installation is complete when:
- ✓ Service starts automatically on boot
- ✓ All buttons respond correctly
- ✓ LEDs illuminate properly
- ✓ Audio transcription captures speech
- ✓ Text-to-speech output is clear
- ✓ LLM responses are generated
- ✓ Conversations are logged
- ✓ System manager shows all components healthy
- ✓ No errors in service logs

---

## Quick Commands Reference

```bash
# Start service
systemctl --user start coyote.service

# Stop service
systemctl --user stop coyote.service

# Restart service
systemctl --user restart coyote.service

# Check status
systemctl --user status coyote.service

# View logs
journalctl --user -u coyote.service -n 50

# Attach to session
b

# Detach from session
Ctrl+B then D

# Run manager
cd ~/coyote_interactive/manager && ./run_manager.py

# Manual run
cd ~/coyote_interactive && source venv/bin/activate && python coyote.py

# Test voice pipeline
echo "I am Wile E. Coyote" | piper --model $PIPER_MODEL_COYOTE -s 71 --length_scale 1.75 --output-raw | sox -t raw -r 22050 -e signed -b 16 -c 1 - -t raw - pitch -200 vol 0.98 | aplay -r 22050 -f S16_LE -t raw
```

---

**Date Completed:** _______________

**Completed By:** _______________

**Notes:**
