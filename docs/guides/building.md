# Building from Source

This guide covers how to build AI-Native OS from source for development or customization.

## Prerequisites

### Build Machine Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Ubuntu 22.04+ / macOS 13+ | Ubuntu 24.04 |
| RAM | 16GB | 32GB |
| Storage | 100GB free | 200GB+ SSD |
| CPU | 4 cores | 8+ cores |

### Required Tools

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
  git \
  build-essential \
  cmake \
  ninja-build \
  python3 \
  python3-pip \
  python3-venv \
  nodejs \
  npm \
  docker.io \
  qemu-user-static \
  binfmt-support

# macOS
brew install \
  git \
  cmake \
  ninja \
  python@3.11 \
  node \
  docker \
  qemu
```

## Repository Structure

```
ainative/
├── build/              # Build scripts and configs
│   ├── buildroot/      # Buildroot configuration
│   ├── docker/         # Docker build environment
│   └── scripts/        # Build automation
├── src/                # AI-Native OS source
│   ├── aios/           # Core orchestrator
│   ├── services/       # s6-rc service definitions
│   └── configs/        # Default configurations
├── packages/           # Pre-built packages
│   ├── vllm/
│   ├── whisper/
│   └── pocket-tts/
├── docs/               # Documentation
└── tools/              # Development tools
```

## Quick Start

### Clone Repository

```bash
git clone https://github.com/raym33/ainative.git
cd ainative
```

### Build Options

```bash
# Option 1: Full image (recommended)
make image TARGET=orangepi5

# Option 2: Development environment
make dev-env

# Option 3: Individual components
make vllm
make whisper
make pocket-tts
make clawdbot
make camel
```

## Building the Full Image

### Step 1: Configure Target

```bash
# List available targets
make list-targets

# Available targets:
# - orangepi5      (Orange Pi 5, 16GB)
# - orangepi5-8gb  (Orange Pi 5, 8GB)
# - rpi5           (Raspberry Pi 5, 8GB)
# - rk3588-generic (Generic RK3588 board)
# - qemu           (QEMU for testing)
```

### Step 2: Download Models

```bash
# Download required models (~7GB total)
make download-models

# Or individually:
make download-model-glm      # GLM-4.6V-Flash (~6GB)
make download-model-whisper  # Whisper small (~500MB)
make download-model-tts      # Pocket-TTS (~100MB)
```

### Step 3: Build Image

```bash
# Full build (takes 30-60 minutes)
make image TARGET=orangepi5

# Build with custom config
make image TARGET=orangepi5 CONFIG=custom.yaml

# Build without models (smaller image)
make image TARGET=orangepi5 INCLUDE_MODELS=no
```

### Step 4: Flash Image

```bash
# List available devices
lsblk

# Flash to SD card or NVMe
make flash DEVICE=/dev/sdX

# Or manually
sudo dd if=build/output/ainative-orangepi5.img of=/dev/sdX bs=4M status=progress
sync
```

## Building Individual Components

### vLLM for ARM64

```bash
cd packages/vllm

# Build in Docker (cross-compile)
docker build -t vllm-arm64 -f Dockerfile.arm64 .

# Extract package
docker cp $(docker create vllm-arm64):/opt/vllm ./dist/
```

### Whisper.cpp

```bash
cd packages/whisper

# Native build (on ARM device)
make -j$(nproc)

# Cross-compile
make CROSS_COMPILE=aarch64-linux-gnu-
```

### Pocket-TTS

```bash
cd packages/pocket-tts

# Create wheel for ARM64
python -m build --wheel

# Or use pre-built
pip download pocket-tts --platform manylinux_2_28_aarch64
```

### Clawdbot

```bash
cd packages/clawdbot

# Install dependencies
pnpm install

# Build
pnpm build

# Package
pnpm pack
```

### CAMEL

```bash
cd packages/camel

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with tools
pip install 'camel-ai[tools]'

# Freeze dependencies
pip freeze > requirements-arm64.txt
```

## Buildroot Configuration

### Customize Buildroot

```bash
# Enter Buildroot menuconfig
make buildroot-menuconfig

# Key options:
# - Target Architecture: AArch64
# - Toolchain: External (Linaro)
# - Init system: s6-rc
# - Root filesystem: ext4
```

### Add Custom Packages

Create `build/buildroot/packages/aios-core/`:

```makefile
# aios-core.mk
AIOS_CORE_VERSION = 1.0.0
AIOS_CORE_SOURCE = aios-core-$(AIOS_CORE_VERSION).tar.gz
AIOS_CORE_SITE = $(call github,raym33,ainative,v$(AIOS_CORE_VERSION))

define AIOS_CORE_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 755 $(@D)/aios $(TARGET_DIR)/usr/bin/aios
    $(INSTALL) -D -m 644 $(@D)/config.yaml $(TARGET_DIR)/etc/aios/config.yaml
endef

$(eval $(generic-package))
```

## Development Environment

### Local Development (No Hardware)

```bash
# Start QEMU environment
make qemu-start

# SSH into VM
ssh -p 2222 root@localhost

# Mount shared folder for development
mount -t 9p -o trans=virtio shared /mnt/shared
```

### On-Device Development

```bash
# Enable development mode on device
aios dev-mode enable

# Sync source files
rsync -avz src/ aios@device:/opt/aios-dev/

# Run development version
ssh aios@device "cd /opt/aios-dev && python -m aios.main"
```

### Docker Development Environment

```bash
# Build development container
make docker-dev

# Run interactive shell
docker run -it --rm \
  -v $(pwd):/workspace \
  -v /dev:/dev \
  --privileged \
  ainative-dev bash
```

## Testing

### Unit Tests

```bash
# Run all tests
make test

# Run specific component tests
make test-aios
make test-camel
make test-voice
```

### Integration Tests

```bash
# Requires QEMU or hardware
make test-integration

# Test specific scenarios
make test-voice-loop
make test-tool-execution
make test-memory
```

### Hardware Tests

```bash
# On target device
aios test hardware

# Tests:
# - CPU performance
# - Memory allocation
# - Storage I/O
# - Network connectivity
# - Audio I/O
```

## Customization

### Custom Agent

Create `src/aios/agents/custom.yaml`:

```yaml
name: custom
description: "My custom agent"
enabled: true

system_prompt: |
  You are a custom agent for specific tasks.

tools:
  - terminal
  - files
  - my_custom_tool

permissions:
  my_custom_tool:
    enabled: true
```

### Custom Tool

Create `src/aios/tools/custom_tool.py`:

```python
from camel.toolkits import BaseToolkit
from camel.functions import OpenAIFunction

class CustomToolkit(BaseToolkit):
    @OpenAIFunction
    def my_custom_function(self, param: str) -> str:
        """Description of what this tool does.

        Args:
            param: Description of parameter
        """
        # Implementation
        return f"Result: {param}"
```

### Custom Service

Create `src/services/custom/run`:

```bash
#!/bin/execlineb -P
fdmove -c 2 1
/usr/bin/python /opt/aios/custom_service.py
```

## Release Process

### Version Bump

```bash
# Bump version
make version-bump VERSION=1.1.0

# Creates:
# - Git tag
# - Updated version files
# - Changelog entry
```

### Build Release

```bash
# Build all targets
make release

# Creates in dist/:
# - ainative-1.1.0-orangepi5.img.xz
# - ainative-1.1.0-rpi5.img.xz
# - ainative-1.1.0-checksums.txt
```

### Publish

```bash
# Upload to GitHub releases
make publish

# Upload to package registry
make publish-packages
```

## Troubleshooting Build Issues

### Out of Memory

```bash
# Reduce parallel jobs
make image TARGET=orangepi5 JOBS=2

# Or increase swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Cross-Compilation Errors

```bash
# Ensure QEMU is set up
docker run --privileged --rm tonistiigi/binfmt --install all

# Verify
cat /proc/sys/fs/binfmt_misc/qemu-aarch64
```

### Missing Dependencies

```bash
# Check build dependencies
make check-deps

# Install missing
make install-deps
```

## Related Documentation

- [Configuration](configuration.md) - Customizing the built image
- [Hardware Guide](hardware.md) - Target device setup
- [Architecture Overview](../architecture/overview.md) - System design
