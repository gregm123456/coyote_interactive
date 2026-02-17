#!/bin/bash
# Coyote Interactive - Automated Installation Script for Raspberry Pi
# This script automates the installation of Coyote Interactive and its dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        log_warn "This doesn't appear to be a Raspberry Pi. Continue anyway? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    sudo apt update
    sudo apt upgrade -y
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    sudo apt install -y \
        python3 python3-pip python3-venv \
        git cmake build-essential wget \
        swig \
        libsdl2-dev \
        pulseaudio pavucontrol \
        network-manager \
        byobu \
        alsa-utils \
        espeak-ng \
        python3-lgpio liblgpio-dev \
        python3-dev pkg-config \
        ffmpeg \
        mpg123 \
        sox
}

# Install whisper.cpp
install_whisper() {
    log_info "Installing whisper.cpp..."
    
    if [ -d "/opt/whisper.cpp" ]; then
        log_warn "Whisper.cpp already exists in /opt/whisper.cpp. Skip? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            return 0
        fi
        sudo rm -rf /opt/whisper.cpp
    fi
    
    sudo git clone https://github.com/ggerganov/whisper.cpp /opt/whisper.cpp
    cd /opt/whisper.cpp
    
    # Create models directory
    sudo mkdir -p /usr/share/whisper/models
    
    # Download whisper models
    log_info "Downloading whisper base.en model..."
    sudo sh ./models/download-ggml-model.sh base.en
    sudo mv models/ggml-base.en.bin /usr/share/whisper/models/
    
    log_info "Downloading whisper tiny.en model (for faster performance if needed)..."
    sudo sh ./models/download-ggml-model.sh tiny.en
    sudo mv models/ggml-tiny.en.bin /usr/share/whisper/models/
    
    # Build whisper.cpp
    log_info "Building whisper.cpp (this may take several minutes)..."
    sudo cmake -B build -DWHISPER_SDL2=ON
    sudo cmake --build build --config Release
    
    # Install binaries
    sudo cp build/bin/* /usr/local/bin/
    sudo chmod +x /usr/local/bin/*
    
    log_info "Whisper.cpp installed successfully"
    cd "$SCRIPT_DIR"
}

# Install Piper TTS
install_piper() {
    log_info "Installing Piper TTS..."
    
    # Detect architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "aarch64" ]; then
        PIPER_ARCH="aarch64"
    elif [ "$ARCH" = "armv7l" ]; then
        PIPER_ARCH="armv7l"
    else
        log_error "Unsupported architecture: $ARCH"
        return 1
    fi
    
    # Create piper directory
    sudo mkdir -p /usr/share/piper/voices
    
    # Download Piper
    cd /tmp
    PIPER_VERSION="2023.11.14-2"
    PIPER_FILE="piper_linux_${PIPER_ARCH}.tar.gz"
    
    log_info "Downloading Piper for ${PIPER_ARCH}..."
    wget -q "https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/${PIPER_FILE}"
    tar -xzf "$PIPER_FILE"
    sudo cp piper/piper /usr/local/bin/
    sudo chmod +x /usr/local/bin/piper
    
    # Copy shared libraries and update loader cache
    log_info "Installing Piper shared libraries..."
    sudo cp piper/lib* /usr/local/lib/ 2>/dev/null || true
    sudo ldconfig
    
    rm -rf piper "$PIPER_FILE"
    
    # Download voice models
    log_info "Downloading Piper voice models..."
    cd /usr/share/piper/voices
    sudo mkdir -p en_GB
    cd en_GB
    
    # Alba voice
    log_info "Downloading alba-medium voice..."
    sudo wget -nc -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx
    sudo wget -nc -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json
    
    # VCTK voice
    log_info "Downloading vctk-medium voice..."
    sudo wget -nc --inet4-only -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx
    sudo wget -nc --inet4-only -q https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx.json
    
    # Cleanup any duplicates from previous failed runs
    sudo rm -f *.onnx.* *.json.*
    
    log_info "Piper TTS installed successfully"
    cd "$SCRIPT_DIR"
}

# Setup Python environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    cd "$SCRIPT_DIR"
    
    # Create virtual environment
    if [ -d "venv" ]; then
        log_warn "Virtual environment already exists. Recreate? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
        fi
    else
        python3 -m venv venv
    fi
    
    # Activate and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install manager package
    log_info "Installing manager package..."
    pip install -e ./manager
    
    log_info "Python environment setup complete"
}

# Configure GPIO permissions
setup_gpio() {
    log_info "Configuring GPIO permissions..."
    sudo usermod -a -G gpio "$USER"
    log_warn "You may need to log out and back in for GPIO group changes to take effect"
}

# Create required directories
create_directories() {
    log_info "Creating required directories..."
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR"
    
    mkdir -p conversation_data
    mkdir -p audio_to_text
    
    log_info "Directories created"
}

# Setup config secrets
setup_config() {
    log_info "Setting up configuration..."
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR"
    
    if [ ! -f "config_secrets.py" ]; then
        cp config_secrets.example.py config_secrets.py
        log_warn "Created config_secrets.py - YOU MUST EDIT THIS FILE with your API credentials!"
        log_warn "Edit: nano config_secrets.py"
    else
        log_info "config_secrets.py already exists"
    fi
}

# Setup environment variables
setup_environment_vars() {
    log_info "Setting up environment variables..."
    
    # Check if environment variables are already set
    if grep -q "PIPER_MODEL_COYOTE" /etc/environment 2>/dev/null; then
        log_info "Environment variables already configured"
    else
        log_warn "Setting up environment variables in /etc/environment"
        echo "PIPER_MODEL=/usr/share/piper/voices/en_GB/en_GB-alba-medium.onnx" | sudo tee -a /etc/environment > /dev/null
        echo "PIPER_MODEL_COYOTE=/usr/share/piper/voices/en_GB/en_GB-vctk-medium.onnx" | sudo tee -a /etc/environment > /dev/null
        log_info "Environment variables set. They will be available after logout/login or reboot"
    fi
}

# Run system configuration check
run_system_check() {
    log_info "Running system configuration check..."
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR/manager"
    
    source ../venv/bin/activate
    python check_system.py
    
    cd -
}

# Setup systemd service
setup_systemd() {
    log_info "Setting up systemd service..."
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    USER_HOME="$HOME"
    
    # Create systemd user directory
    mkdir -p ~/.config/systemd/user/
    
    # Copy and update service file
    log_info "Creating systemd service file..."
    sed -e "s|/home/robot|$USER_HOME|g" \
        -e "s|USER=robot|USER=$USER|g" \
        -e "s|LOGNAME=robot|LOGNAME=$USER|g" \
        "$SCRIPT_DIR/coyote.service" > ~/.config/systemd/user/coyote.service
    
    # Reload systemd
    systemctl --user daemon-reload
    
    # Enable service
    systemctl --user enable coyote.service
    
    # Enable lingering
    sudo loginctl enable-linger "$USER"
    
    # Add byobu alias
    if ! grep -q "alias b='byobu attach -t coyote_session'" ~/.bashrc; then
        echo "alias b='byobu attach -t coyote_session'" >> ~/.bashrc
        log_info "Added byobu alias to ~/.bashrc"
    fi
    
    log_info "Systemd service configured"
    log_warn "Service will NOT be started automatically by this script"
    log_info "To start: systemctl --user start coyote.service"
}

# Main installation flow
main() {
    log_info "Starting Coyote Interactive installation..."
    echo ""
    
    check_raspberry_pi
    
    log_info "This script will install all dependencies for Coyote Interactive."
    log_info "The installation may take 30-60 minutes depending on your Pi model."
    echo ""
    read -p "Continue with installation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled"
        exit 0
    fi
    
    # Installation steps
    update_system
    install_system_deps
    install_whisper
    install_piper
    setup_environment_vars
    setup_python_env
    setup_gpio
    create_directories
    setup_config
    
    log_info ""
    log_info "Running system configuration check..."
    run_system_check
    
    log_info ""
    log_warn "Do you want to set up the systemd service for auto-start? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        setup_systemd
    fi
    
    # Installation complete
    echo ""
    log_info "=========================================="
    log_info "Installation Complete!"
    log_info "=========================================="
    echo ""
    log_warn "IMPORTANT NEXT STEPS:"
    echo ""
    echo "1. Edit configuration file with your API credentials:"
    echo "   nano ~/coyote_interactive/config_secrets.py"
    echo ""
    echo "2. Log out and back in for GPIO permissions to take effect"
    echo ""
    echo "3. Test the installation manually:"
    echo "   cd ~/coyote_interactive"
    echo "   source venv/bin/activate"
    echo "   python coyote.py"
    echo ""
    echo "4. Start the systemd service:"
    echo "   systemctl --user start coyote.service"
    echo ""
    echo "5. Check service status:"
    echo "   systemctl --user status coyote.service"
    echo ""
    echo "6. Attach to running session:"
    echo "   b  (or: byobu attach -t coyote_session)"
    echo ""
    echo "7. Test the system manager:"
    echo "   cd ~/coyote_interactive/manager"
    echo "   ./run_manager.py"
    echo ""
    log_info "For detailed instructions, see INSTALL.md"
    echo ""
}

# Run main installation
main
