# AI-Native OS - Complete Implementation Guide

**Version:** 1.0
**Date:** January 2026
**For:** Developers & System Architects

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Phase 1: Core Foundation](#phase-1-core-foundation)
5. [Phase 2: Voice Integration](#phase-2-voice-integration)
6. [Phase 3: Messaging Integration](#phase-3-messaging-integration)
7. [Phase 4: Memory Layer](#phase-4-memory-layer)
8. [Phase 5: ARM Image Build](#phase-5-arm-image-build)
9. [Testing & Validation](#testing--validation)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## Executive Summary

### What is AI-Native OS?

AI-Native OS is a minimal operating system for ARM devices where AI is the primary interface. Instead of a traditional desktop with apps, users interact naturally through voice, chat, and vision with an AI that can see, hear, and control the entire system.

### Key Innovation

**Single Model Architecture**: Unlike traditional systems that bolt AI onto an existing OS, we use one powerful model (GLM-4.6V-Flash) that combines:
- **Vision** - Can see screen/camera
- **Tool Use** - Can execute system commands
- **Reasoning** - Can plan multi-step tasks

### Target Hardware

- **Recommended**: Orange Pi 5 (16GB RAM) - $150
- **Minimum**: Raspberry Pi 5 (8GB RAM) - $80
- **Optimal**: Any RK3588 board with 16-32GB RAM

### Technology Stack

| Layer | Component | Size | Purpose |
|-------|-----------|------|---------|
| Interface | Clawdbot | ~150MB | Multi-platform messaging |
| Voice | Whisper.cpp + Pocket-TTS | ~650MB | Speech I/O |
| Orchestration | CAMEL | ~150MB | Multi-agent framework |
| Model | GLM-4.6V-Flash | ~6GB | AI inference |
| Memory | Memos + Qdrant | ~150MB | Persistent storage |
| System | Linux ARM64 | ~100MB | Minimal kernel |

**Total RAM**: ~7.5GB (fits on 8GB device with optimization)

---

## System Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  Voice (Whisper + TTS) • WhatsApp • Telegram • Discord     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 CLAWDBOT GATEWAY                            │
│           WebSocket on port 18789                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  CAMEL ORCHESTRATOR                         │
│    System Agent • Assistant Agent • Browser Agent           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│             GLM-4.6V-FLASH (vLLM Server)                    │
│          Vision + Tools + Reasoning (9B params)             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     TOOLS LAYER                             │
│  Terminal • Files • Browser • Network • System              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  MEMORY LAYER                               │
│      Memos (SQLite) + Qdrant (Vector Store)                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              LINUX ARM64 KERNEL                             │
│          Buildroot • s6-rc init • musl libc                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User speaks → Whisper.cpp → Text
2. Text → Clawdbot → CAMEL → Enriched with memory
3. CAMEL → GLM-4.6V-Flash → Decides action
4. Model calls tool (e.g., "execute ls command")
5. Tool executes → Returns result
6. Model generates response
7. Response → Pocket-TTS → Voice output
8. Interaction saved to Memos
```

---

## Prerequisites

### Development Machine

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Ubuntu 22.04+ / macOS 13+ | Ubuntu 24.04 |
| RAM | 16GB | 32GB |
| Storage | 100GB free | 200GB SSD |
| CPU | 4 cores | 8+ cores |

### Required Software

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
    git \
    build-essential \
    cmake \
    python3.11 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    docker.io \
    qemu-user-static

# macOS
brew install \
    git \
    cmake \
    python@3.11 \
    node \
    docker \
    qemu
```

### Target Device (ARM Board)

- Orange Pi 5 (16GB) or Raspberry Pi 5 (8GB)
- MicroSD card or NVMe SSD (128GB+)
- USB microphone (e.g., ReSpeaker USB)
- USB speaker or 3.5mm audio
- Ethernet cable (WiFi setup comes later)
- 5V/4A power supply

---

## Phase 1: Core Foundation

**Goal**: Create a working Python-based AI orchestrator that runs on any Linux machine.

### Step 1.1: Repository Setup

```bash
# Clone repository
git clone https://github.com/raym33/ainative.git
cd ainative

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install \
    camel-ai[tools] \
    pyyaml \
    click \
    rich \
    httpx \
    pytest
```

### Step 1.2: Create Project Structure

```bash
# Already exists in repo, but for reference:
mkdir -p src/aios/{agents,tools,memory}
touch src/aios/__init__.py
touch src/aios/__main__.py
touch src/aios/core.py
touch src/aios/config.py
touch src/aios/cli.py
```

### Step 1.3: Implement Core Orchestrator

File: `src/aios/core.py`

```python
"""
Main AIOS orchestrator.
Coordinates agents, tools, and memory.
"""

from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.agents import ChatAgent
from aios.config import Config
from aios.tools import TerminalToolkit, FilesToolkit
from typing import Optional, Dict, Any


class AIOS:
    """Main AI-Native OS orchestrator."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize AIOS with configuration."""
        self.config = config or Config.load()
        self.model = self._create_model()
        self.agents = self._create_agents()
        self.conversation_history = []

    def _create_model(self):
        """Create the inference model backend."""
        backend_type = (
            ModelPlatformType.VLLM
            if self.config.inference.backend == "vllm"
            else ModelPlatformType.OLLAMA
        )

        return ModelFactory.create(
            model_platform=backend_type,
            model_type=self.config.inference.model,
            url=self.config.inference.url,
        )

    def _create_agents(self) -> Dict[str, ChatAgent]:
        """Create specialized agents."""
        agents = {}

        # System Agent
        if self.config.agents.get("system", {}).enabled:
            terminal = TerminalToolkit(
                allowed_commands=self.config.tools.terminal["allowed_commands"],
                blocked_commands=self.config.tools.terminal["blocked_commands"],
            )
            files = FilesToolkit(
                allowed_paths=self.config.tools.files["allowed_paths"],
                blocked_paths=self.config.tools.files["blocked_paths"],
            )

            agents["system"] = ChatAgent(
                system_message="""You are the System Agent for AI-Native OS.

Your responsibilities:
- Execute terminal commands
- Manage files and directories
- Monitor system resources
- Answer questions about the system

Rules:
- Always explain what you're doing before executing commands
- Never run destructive commands without explicit confirmation
- Be helpful, accurate, and safe""",
                model=self.model,
                tools=terminal.get_tools() + files.get_tools()
            )

        # Assistant Agent (basic, no tools for now)
        if self.config.agents.get("assistant", {}).enabled:
            agents["assistant"] = ChatAgent(
                system_message="""You are a helpful personal assistant.

You help with:
- Answering questions
- Providing information
- Having friendly conversations
- Helping with daily tasks

Be concise, friendly, and helpful.""",
                model=self.model,
            )

        return agents

    def chat(self, message: str, agent_name: str = "system") -> str:
        """Send a message and get a response.

        Args:
            message: User message
            agent_name: Which agent to use (default: system)

        Returns:
            AI response
        """
        agent = self.agents.get(agent_name)
        if not agent:
            return f"Error: Agent '{agent_name}' not found. Available: {list(self.agents.keys())}"

        try:
            # Add to history
            self.conversation_history.append({
                "role": "user",
                "content": message
            })

            # Get response
            response = agent.step(message)
            response_text = response.msgs[0].content if response.msgs else "No response"

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            return response_text

        except Exception as e:
            return f"Error: {str(e)}"

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        for agent in self.agents.values():
            agent.reset()

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "config": self.config.to_dict(),
            "agents": list(self.agents.keys()),
            "model": self.config.inference.model,
            "backend": self.config.inference.backend,
            "conversation_length": len(self.conversation_history),
        }
```

### Step 1.4: Implement CLI

File: `src/aios/cli.py`

```python
"""
Command-line interface for AIOS.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from aios import AIOS, Config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI-Native OS - Command Line Interface"""
    pass


@cli.command()
@click.argument("message", nargs=-1)
@click.option("--agent", default="system", help="Agent to use")
@click.option("--config", type=click.Path(), help="Config file path")
def chat(message, agent, config):
    """Send a message to the AI.

    Example: aios chat "list files in current directory"
    """
    try:
        aios = AIOS(config=Config.load(config) if config else None)
        user_message = " ".join(message)

        console.print(f"[bold blue]You:[/bold blue] {user_message}")

        response = aios.chat(user_message, agent_name=agent)

        console.print(Panel(
            Markdown(response),
            title=f"[bold green]AI ({agent})[/bold green]",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.option("--agent", default="system", help="Agent to use")
@click.option("--config", type=click.Path(), help="Config file path")
def interactive(agent, config):
    """Start an interactive chat session."""
    try:
        aios = AIOS(config=Config.load(config) if config else None)

        console.print(Panel(
            "[bold green]AI-Native OS Interactive Mode[/bold green]\n"
            "Type your messages and press Enter.\n"
            "Commands: /quit, /reset, /status",
            border_style="green"
        ))

        while True:
            user_input = console.input("[bold blue]You:[/bold blue] ")

            if user_input.lower() in ["/quit", "/exit", "/q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif user_input.lower() == "/reset":
                aios.reset_conversation()
                console.print("[yellow]Conversation reset.[/yellow]")
                continue
            elif user_input.lower() == "/status":
                status = aios.get_status()
                console.print(status)
                continue

            if not user_input.strip():
                continue

            response = aios.chat(user_input, agent_name=agent)

            console.print(Panel(
                Markdown(response),
                title=f"[bold green]AI ({agent})[/bold green]",
                border_style="green"
            ))

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.option("--config", type=click.Path(), help="Config file path")
def status(config):
    """Show AIOS status."""
    try:
        aios = AIOS(config=Config.load(config) if config else None)
        status_info = aios.get_status()

        console.print(Panel(
            f"""[bold]System Status[/bold]

Model: {status_info['model']}
Backend: {status_info['backend']}
Agents: {', '.join(status_info['agents'])}
Conversation Length: {status_info['conversation_length']}
""",
            border_style="blue"
        ))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
def config_show():
    """Show current configuration."""
    try:
        config = Config.load()
        import yaml
        console.print(yaml.dump(config.to_dict(), default_flow_style=False))
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    cli()
```

### Step 1.5: Create Entry Point

File: `src/aios/__main__.py`

```python
"""
Main entry point for AIOS.
Allows running: python -m aios
"""

from aios.cli import cli

if __name__ == "__main__":
    cli()
```

### Step 1.6: Create Configuration File

File: `config.yaml` (in project root)

```yaml
system:
  name: "AIOS"
  language: "en"
  log_level: "info"

inference:
  backend: "ollama"  # Change to "vllm" when ready
  model: "llama3.2"  # Start with llama for testing
  url: "http://localhost:11434/v1"
  max_tokens: 4096
  temperature: 0.8

agents:
  system:
    enabled: true
    tools: ["terminal", "files"]
  assistant:
    enabled: true
    tools: []

tools:
  terminal:
    allowed_commands: ["ls", "cat", "pwd", "echo", "date", "whoami", "df", "free"]
    blocked_commands: ["rm -rf", "dd", "mkfs"]
    timeout: 30
  files:
    allowed_paths:
      - "/home"
      - "/tmp"
    blocked_paths:
      - "/etc"
      - "/boot"
      - "/root"
```

### Step 1.7: Create Package Configuration

File: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ainative"
version = "0.1.0"
description = "AI-Native Operating System"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "AI-Native OS Contributors"}
]
dependencies = [
    "camel-ai[tools]>=0.2.0",
    "pyyaml>=6.0",
    "click>=8.0",
    "rich>=13.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
]

[project.scripts]
aios = "aios.cli:cli"

[tool.setuptools]
packages = ["aios", "aios.agents", "aios.tools", "aios.memory"]
package-dir = {"" = "src"}
```

File: `requirements.txt`

```
camel-ai[tools]>=0.2.0
pyyaml>=6.0
click>=8.0
rich>=13.0
httpx>=0.25.0
```

### Step 1.8: Test Basic Functionality

```bash
# Install Ollama (for testing)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a test model
ollama pull llama3.2

# Install AIOS in development mode
pip install -e .

# Test CLI
aios status

# Test interactive mode
aios interactive

# Example interaction:
# You: List files in the current directory
# AI: [uses terminal tool to run 'ls -la']
# AI: I found 15 files in the current directory:
#     - README.md (4.5 KB)
#     - config.yaml (1.2 KB)
#     ...

# You: Create a test file called hello.txt with the content "Hello, World!"
# AI: [uses files tool to write file]
# AI: Successfully written to hello.txt

# You: Read the file you just created
# AI: [uses files tool to read]
# AI: The file contains: "Hello, World!"
```

### Step 1.9: Validation Checklist

- [ ] CLI runs without errors (`aios status`)
- [ ] Can send single messages (`aios chat "hello"`)
- [ ] Interactive mode works (`aios interactive`)
- [ ] Terminal tool executes commands (test `ls`)
- [ ] File tool can read/write files
- [ ] Agent remembers conversation context
- [ ] Configuration loads correctly
- [ ] Error handling works (try invalid commands)

---

## Phase 2: Voice Integration

**Goal**: Add speech-to-text and text-to-speech capabilities.

### Step 2.1: Install Whisper.cpp

```bash
# Clone and build
cd ~/
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make

# Download model (small = 500MB)
bash ./models/download-ggml-model.sh small

# Test
./main -m models/ggml-small.bin -f samples/jfk.wav

# Build server
make server

# Start server (in background)
./server -m models/ggml-small.bin --port 8081 &
```

### Step 2.2: Install Pocket-TTS

```bash
# Install
pip install pocket-tts

# Test
python -c "from pocket_tts import PocketTTS; tts = PocketTTS(); tts.synthesize('Hello, this is a test.').save('test.wav')"

# Play test
aplay test.wav  # Linux
# or
afplay test.wav  # macOS

# Start server
pocket-tts-serve --port 8080 &
```

### Step 2.3: Create Voice Module

File: `src/aios/voice.py`

```python
"""
Voice I/O module for AI-Native OS.
"""

import httpx
import sounddevice as sd
import numpy as np
import wave
import tempfile
from pathlib import Path


class VoiceIO:
    """Handle speech-to-text and text-to-speech."""

    def __init__(
        self,
        stt_url: str = "http://localhost:8081",
        tts_url: str = "http://localhost:8080",
        tts_voice: str = "alba",
        sample_rate: int = 16000,
    ):
        self.stt_url = stt_url
        self.tts_url = tts_url
        self.tts_voice = tts_voice
        self.sample_rate = sample_rate
        self.client = httpx.Client(timeout=30.0)

    def record_audio(self, duration: int = 5) -> bytes:
        """Record audio from microphone.

        Args:
            duration: Recording duration in seconds

        Returns:
            WAV audio data
        """
        print(f"Recording for {duration} seconds...")
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()

        # Convert to WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())

        with open(temp_path, 'rb') as f:
            wav_data = f.read()

        Path(temp_path).unlink()
        return wav_data

    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio to text.

        Args:
            audio_data: WAV audio data

        Returns:
            Transcribed text
        """
        response = self.client.post(
            f"{self.stt_url}/inference",
            files={"file": ("audio.wav", audio_data, "audio/wav")}
        )
        response.raise_for_status()
        return response.json()["text"]

    def synthesize(self, text: str) -> bytes:
        """Convert text to speech.

        Args:
            text: Text to synthesize

        Returns:
            WAV audio data
        """
        response = self.client.post(
            f"{self.tts_url}/synthesize",
            json={"text": text, "voice": self.tts_voice}
        )
        response.raise_for_status()
        return response.content

    def speak(self, text: str):
        """Synthesize and play audio.

        Args:
            text: Text to speak
        """
        audio_data = self.synthesize(text)

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        # Play
        data, fs = self._load_wav(temp_path)
        sd.play(data, fs)
        sd.wait()

        Path(temp_path).unlink()

    def _load_wav(self, path: str):
        """Load WAV file."""
        with wave.open(path, 'rb') as wf:
            sample_rate = wf.getframerate()
            data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        return data, sample_rate

    def voice_loop(self, aios_instance):
        """Run continuous voice interaction loop.

        Args:
            aios_instance: AIOS instance to send messages to
        """
        print("Voice loop starting. Press Ctrl+C to exit.")
        self.speak("AI OS ready. How can I help you?")

        try:
            while True:
                # Record
                audio = self.record_audio(duration=5)

                # Transcribe
                text = self.transcribe(audio)
                if not text.strip():
                    continue

                print(f"You: {text}")

                # Process with AI
                response = aios_instance.chat(text)
                print(f"AI: {response}")

                # Speak response
                self.speak(response)

        except KeyboardInterrupt:
            self.speak("Goodbye!")
            print("\nVoice loop stopped.")
```

### Step 2.4: Add Voice Command to CLI

Update `src/aios/cli.py`:

```python
# Add this command

@cli.command()
@click.option("--config", type=click.Path(), help="Config file path")
def voice(config):
    """Start voice interaction mode."""
    try:
        from aios.voice import VoiceIO

        console.print("[bold green]Starting voice mode...[/bold green]")
        console.print("Make sure Whisper and Pocket-TTS servers are running!")

        aios = AIOS(config=Config.load(config) if config else None)
        voice_io = VoiceIO()

        voice_io.voice_loop(aios)

    except ImportError:
        console.print("[red]Voice dependencies not installed.[/red]")
        console.print("Install: pip install sounddevice numpy")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
```

### Step 2.5: Test Voice System

```bash
# Install audio dependencies
pip install sounddevice numpy

# Make sure services are running
pgrep -f whisper  # Should show process
pgrep -f pocket-tts  # Should show process

# Test voice mode
aios voice

# Expected flow:
# 1. "AI OS ready. How can I help you?" (spoken)
# 2. Recording for 5 seconds...
# 3. You: "list files"
# 4. AI: "I found 12 files..." (spoken)
```

---

## Phase 3: Messaging Integration

**Goal**: Connect Clawdbot for multi-platform messaging.

### Step 3.1: Fork and Install Clawdbot

```bash
cd ~/
git clone https://github.com/clawdbot/clawdbot.git
cd clawdbot

# Install dependencies
pnpm install

# Build
pnpm build
```

### Step 3.2: Modify Clawdbot for Local Model

Edit `clawdbot/src/ai/client.ts`:

```typescript
// Replace Anthropic API with local vLLM/Ollama

export async function callLocalAI(messages: Message[]): Promise<string> {
  const response = await fetch('http://localhost:11434/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llama3.2',
      messages: messages,
    }),
  });

  const data = await response.json();
  return data.choices[0].message.content;
}
```

### Step 3.3: Create Bridge Service

File: `src/aios/bridge.py`

```python
"""
Bridge between Clawdbot gateway and AIOS.
"""

import asyncio
import websockets
import json
from aios import AIOS


class ClawdbotBridge:
    """Bridge Clawdbot WebSocket to AIOS."""

    def __init__(self, aios: AIOS, gateway_url: str = "ws://localhost:18789"):
        self.aios = aios
        self.gateway_url = gateway_url

    async def handle_message(self, websocket):
        """Handle incoming messages from Clawdbot."""
        async for message in websocket:
            try:
                data = json.loads(message)

                if data.get("type") == "message":
                    user_message = data.get("text", "")
                    channel = data.get("channel", "unknown")
                    user_id = data.get("user_id", "unknown")

                    # Process with AIOS
                    response = self.aios.chat(user_message)

                    # Send response back
                    await websocket.send(json.dumps({
                        "type": "response",
                        "channel": channel,
                        "user_id": user_id,
                        "text": response
                    }))

            except Exception as e:
                print(f"Error handling message: {e}")

    async def run(self):
        """Start the bridge server."""
        async with websockets.serve(self.handle_message, "localhost", 18790):
            print("Bridge running on ws://localhost:18790")
            await asyncio.Future()  # Run forever
```

### Step 3.4: Start Complete Stack

```bash
# Terminal 1: Start Clawdbot
cd ~/clawdbot
pnpm start

# Terminal 2: Start AIOS bridge
cd ~/ainative
python -c "
from aios import AIOS
from aios.bridge import ClawdbotBridge
import asyncio

aios = AIOS()
bridge = ClawdbotBridge(aios)
asyncio.run(bridge.run())
"

# Terminal 3: Test via WhatsApp or Telegram
# (Configure in Clawdbot first)
```

---

## Phase 4: Memory Layer

**Goal**: Add persistent memory with Memos and vector search.

### Step 4.1: Install Memos

```bash
# Using Docker
docker run -d \
  --name memos \
  -p 5230:5230 \
  -v ~/.aios/memos:/var/opt/memos \
  ghcr.io/usememos/memos:latest

# Or download binary
wget https://github.com/usememos/memos/releases/latest/download/memos-linux-amd64
chmod +x memos-linux-amd64
./memos-linux-amd64 --mode prod --port 5230 &
```

### Step 4.2: Install Qdrant

```bash
# Using Docker
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v ~/.aios/qdrant:/qdrant/storage \
  qdrant/qdrant
```

### Step 4.3: Create Memory Module

File: `src/aios/memory/persistent.py`

```python
"""
Persistent memory using Memos and Qdrant.
"""

import httpx
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional


class PersistentMemory:
    """Persistent memory backend."""

    def __init__(
        self,
        memos_url: str = "http://localhost:5230",
        qdrant_path: str = "~/.aios/qdrant",
        memos_token: Optional[str] = None,
    ):
        self.memos_url = memos_url
        self.memos_token = memos_token
        self.client = httpx.Client(timeout=10.0)

        # Vector search
        self.qdrant = QdrantClient(path=qdrant_path)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        # Create collection if not exists
        try:
            self.qdrant.create_collection(
                collection_name="conversations",
                vectors_config={"size": 384, "distance": "Cosine"}
            )
        except:
            pass  # Collection already exists

    def save_conversation(self, user_input: str, ai_response: str, metadata: Dict = None):
        """Save a conversation turn."""
        content = f"User: {user_input}\nAI: {ai_response}"

        # Save to Memos
        headers = {}
        if self.memos_token:
            headers["Authorization"] = f"Bearer {self.memos_token}"

        self.client.post(
            f"{self.memos_url}/api/v1/memos",
            json={"content": content, "visibility": "PRIVATE"},
            headers=headers
        )

        # Save to vector store
        embedding = self.encoder.encode(content)
        self.qdrant.upsert(
            collection_name="conversations",
            points=[{
                "id": hash(content),
                "vector": embedding.tolist(),
                "payload": {
                    "user_input": user_input,
                    "ai_response": ai_response,
                    "metadata": metadata or {}
                }
            }]
        )

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for relevant past conversations."""
        query_embedding = self.encoder.encode(query)

        results = self.qdrant.search(
            collection_name="conversations",
            query_vector=query_embedding.tolist(),
            limit=limit
        )

        return [
            {
                "user_input": hit.payload["user_input"],
                "ai_response": hit.payload["ai_response"],
                "score": hit.score
            }
            for hit in results
        ]
```

### Step 4.4: Integrate Memory into AIOS

Update `src/aios/core.py`:

```python
# Add memory initialization in __init__:

from aios.memory.persistent import PersistentMemory

def __init__(self, config: Optional[Config] = None):
    # ... existing code ...

    # Initialize memory
    if self.config.memory.backend == "memos":
        self.memory = PersistentMemory(
            memos_url=self.config.memory.memos_url
        )
    else:
        self.memory = None

# Update chat method to use memory:

def chat(self, message: str, agent_name: str = "system") -> str:
    # ... get response ...

    # Save to memory
    if self.memory:
        self.memory.save_conversation(message, response_text)

    return response_text
```

---

## Phase 5: ARM Image Build

**Goal**: Create bootable image for ARM devices.

### Step 5.1: Set Up Buildroot

```bash
cd ~/
wget https://buildroot.org/downloads/buildroot-2024.02.tar.gz
tar -xzf buildroot-2024.02.tar.gz
cd buildroot-2024.02

# Start configuration
make menuconfig
```

### Step 5.2: Configure Buildroot

Key settings:

```
Target options:
  Target Architecture: AArch64 (little endian)
  Target Architecture Variant: cortex-a76.cortex-a55

Toolchain:
  Toolchain type: External toolchain
  Toolchain: Linaro AArch64 2023.09

System configuration:
  Init system: Custom scripts
  /dev management: Dynamic using devtmpfs + mdev
  Root filesystem overlay: ../ainative/overlay/

Kernel:
  Linux Kernel: 6.6.x
  Kernel configuration: Using a custom config file

Filesystem images:
  ext4 root filesystem
  tar the root filesystem

Target packages:
  - Python 3.11
  - Node.js 20
  - OpenSSL
  - ALSA utils
```

### Step 5.3: Create Root Filesystem Overlay

```bash
cd ~/ainative
mkdir -p overlay/etc/aios
mkdir -p overlay/opt
mkdir -p overlay/etc/s6-rc

# Copy AIOS
cp -r src overlay/opt/aios

# Copy configuration
cp config.yaml overlay/etc/aios/

# Copy models (will be large)
cp -r ~/whisper.cpp/models overlay/opt/whisper/
```

### Step 5.4: Create s6-rc Services

File: `overlay/etc/s6-rc/vllm/run`

```bash
#!/bin/execlineb -P
fdmove -c 2 1
cd /opt/vllm
python -m vllm.entrypoints.openai.api_server \
  --model /var/aios/models/glm-4.6v-flash \
  --quantization awq \
  --port 8000
```

File: `overlay/etc/s6-rc/whisper/run`

```bash
#!/bin/execlineb -P
fdmove -c 2 1
/opt/whisper/server \
  -m /opt/whisper/models/ggml-small.bin \
  --port 8081
```

File: `overlay/etc/s6-rc/aios/run`

```bash
#!/bin/execlineb -P
fdmove -c 2 1
cd /opt/aios
python -m aios interactive
```

### Step 5.5: Build Image

```bash
cd ~/buildroot-2024.02
make

# Output will be in output/images/
# - sdcard.img (flashable image)
# - rootfs.tar (root filesystem)
```

### Step 5.6: Flash to Device

```bash
# Insert SD card or connect NVMe via USB adapter
# Find device
lsblk

# Flash (replace sdX with your device)
sudo dd if=output/images/sdcard.img of=/dev/sdX bs=4M status=progress
sync

# Eject and insert into ARM board
```

---

## Testing & Validation

### Unit Tests

```bash
cd ~/ainative
pytest tests/
```

### Integration Tests

```bash
# Test voice pipeline
aios voice

# Test messaging
# Send WhatsApp message → should get response

# Test tools
aios chat "list files"
aios chat "create a file test.txt with content hello"
aios chat "read test.txt"
```

### Hardware Tests

On ARM device:

```bash
# Check services
s6-svstat /run/service/*

# Test model
curl http://localhost:8000/health

# Test voice
arecord -d 3 test.wav
aplay test.wav

# Test AIOS
aios status
```

---

## Deployment

### Production Checklist

- [ ] All services start automatically
- [ ] Voice wake word configured
- [ ] Messaging platforms linked
- [ ] Memory backends initialized
- [ ] Monitoring enabled
- [ ] Backups configured
- [ ] Security hardened

### Monitoring

```bash
# System health endpoint
curl http://localhost:9090/health

# Service logs
tail -f /var/log/aios/*.log

# Resource usage
htop
```

---

## Troubleshooting

### Model Won't Load

```bash
# Check memory
free -h

# Reduce quantization
# Edit config: quantization: Q4_K_S

# Check model path
ls -lh /var/aios/models/
```

### Voice Not Working

```bash
# Test microphone
arecord -d 3 test.wav

# Test speaker
aplay /usr/share/sounds/alsa/Front_Center.wav

# Check services
curl http://localhost:8081/health  # Whisper
curl http://localhost:8080/health  # TTS
```

### Slow Inference

```bash
# Check CPU usage
htop

# Enable NPU acceleration (RK3588)
# Add to config: use_npu: true

# Reduce context length
# Edit config: max_model_len: 16384
```

---

## Next Steps

1. **Optimize boot time** - Parallel service startup
2. **Add GUI** - Optional WebKit-based interface
3. **Home Assistant integration** - Control smart home
4. **Plugin system** - Community extensions
5. **Mobile app** - iOS/Android companion

---

## Support & Resources

- **Documentation**: https://github.com/raym33/ainative/docs
- **Issues**: https://github.com/raym33/ainative/issues
- **Discussions**: https://github.com/raym33/ainative/discussions
- **Discord**: Coming soon

---

**AI-Native OS** - *The operating system that listens, sees, and acts.*

Implementation guide version 1.0 - January 2026
