#!/bin/bash

# ============================================================================
# Podman Setup Script for Speech-to-Text Service
# ============================================================================

set -e

echo "🚀 Setting up Speech-to-Text Service with Podman"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for rootless Podman setup"
        echo "Run as regular user: ./podman-setup.sh"
        exit 1
    fi
}

# Install Podman if not present
install_podman() {
    print_status "Checking Podman installation..."
    
    if ! command -v podman &> /dev/null; then
        print_status "Installing Podman..."
        
        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            OS=$ID
        else
            print_error "Cannot detect OS"
            exit 1
        fi
        
        case $OS in
            "ubuntu"|"debian")
                sudo apt update
                sudo apt install -y podman podman-compose
                ;;
            "fedora")
                sudo dnf install -y podman podman-compose
                ;;
            "arch")
                sudo pacman -S podman podman-compose
                ;;
            *)
                print_error "Unsupported OS: $OS"
                exit 1
                ;;
        esac
        
        print_success "Podman installed successfully"
    else
        print_success "Podman is already installed"
    fi
}

# Setup Podman for rootless operation
setup_rootless() {
    print_status "Setting up rootless Podman..."
    
    sudo loginctl enable-linger $(whoami)
    
    if ! grep -q "$(whoami)" /etc/subuid; then
        print_status "Configuring subuid/subgid..."
        echo "$(whoami):100000:65536" | sudo tee -a /etc/subuid
        echo "$(whoami):100000:65536" | sudo tee -a /etc/subgid
        podman system migrate
    fi
    
    print_success "Rootless Podman configured"
}

# Setup NVIDIA GPU support for Podman
setup_gpu_support() {
    print_status "Setting up GPU support..."
    
    if ! command -v nvidia-container-runtime &> /dev/null; then
        print_status "Installing NVIDIA Container Toolkit..."
        
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
        && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
        && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
                sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
                sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        
        sudo apt update
        sudo apt install -y nvidia-container-toolkit
        sudo nvidia-ctk runtime configure --runtime=crun --config=/usr/share/containers/containers.conf
        
        print_success "GPU support configured"
    else
        print_success "GPU support already configured"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating project directories..."
    mkdir -p logs data models
    print_success "Directories created"
}

# Build the container image
build_image() {
    print_status "Building STT service container image..."
    podman build -t stt-service:latest .
    print_success "Container image built successfully"
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    mkdir -p ~/.config/systemd/user
    
    cat > ~/.config/systemd/user/stt-service.service << EOF
[Unit]
Description=Speech-to-Text Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/podman-compose -f ${PWD}/docker-compose.yml up
ExecStop=/usr/bin/podman-compose -f ${PWD}/docker-compose.yml down
Restart=on-failure
RestartSec=5
Environment=PODMAN_USERNS=keep-id

[Install]
WantedBy=default.target
EOF
    
    systemctl --user daemon-reload
    systemctl --user enable stt-service.service
    
    print_success "Systemd service created and enabled"
}

# Setup audio permissions
setup_audio() {
    print_status "Setting up audio permissions..."
    
    sudo usermod -a -G audio $(whoami)
    echo 'SUBSYSTEM=="sound", GROUP="audio", MODE="0664"' | sudo tee /etc/udev/rules.d/99-audio-containers.rules
    sudo udevadm control --reload-rules
    
    print_warning "Please log out and back in for audio group changes to take effect"
    print_success "Audio permissions configured"
}

# Main setup function
main() {
    echo "Starting Podman setup for Speech-to-Text Service..."
    echo
    
    check_root
    install_podman
    setup_rootless
    
    if command -v nvidia-smi &> /dev/null; then
        print_status "NVIDIA GPU detected"
        setup_gpu_support
    else
        print_warning "No NVIDIA GPU detected, skipping GPU setup"
    fi
    
    create_directories
    build_image
    setup_audio
    create_systemd_service
    
    echo
    print_success "=== Setup Complete! ==="
    echo
    echo "Next steps:"
    echo "1. Log out and back in (for audio group changes)"
    echo "2. Start the service: systemctl --user start stt-service"
    echo "3. Check status: systemctl --user status stt-service"
    echo "4. View logs: podman-compose logs -f stt-service"
    echo "5. Stop service: systemctl --user stop stt-service"
    echo
    echo "Service URLs:"
    echo "- STT Service: http://localhost:8080"
    echo "- Database: localhost:5432"
    echo "- Redis: localhost:6379"
    echo
}

main "$@"