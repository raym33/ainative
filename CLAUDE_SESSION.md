# AI-Native OS - Development Session Context

> **Purpose**: This file maintains context for Claude to continue development across sessions.
> **Last Updated**: 2025-01-18
> **Current Phase**: Phase 1 - Foundation

---

## Project Overview

Building a minimal AI-native operating system for ARM chips that combines:
- **Clawdbot** - Multi-platform messaging gateway
- **CAMEL** - Multi-agent orchestration framework
- **GLM-4.6V-Flash** - Vision + Tools + Reasoning model (9B params)
- **Whisper.cpp** - Local speech-to-text
- **Pocket-TTS** - Local text-to-speech
- **Memos** - Knowledge base and memory

Target hardware: Orange Pi 5 (16GB), Raspberry Pi 5 (8GB), RK3588 boards

---

## Repository Structure

```
ainative/
├── docs/                    # ✅ COMPLETED
│   ├── README.md
│   ├── FEATURES.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── data-flow.md
│   │   └── stack.md
│   ├── components/
│   │   ├── clawdbot.md
│   │   ├── camel.md
│   │   ├── glm-model.md
│   │   ├── voice.md
│   │   └── memos.md
│   └── guides/
│       ├── configuration.md
│       ├── boot-sequence.md
│       ├── hardware.md
│       └── building.md
├── src/                     # 🔲 TO BUILD
│   ├── aios/                # Core orchestrator
│   ├── services/            # s6-rc service definitions
│   └── configs/             # Default configurations
├── packages/                # 🔲 TO BUILD
│   ├── vllm/
│   ├── whisper/
│   └── pocket-tts/
├── build/                   # 🔲 TO BUILD
│   ├── buildroot/
│   ├── docker/
│   └── scripts/
├── CLAUDE_SESSION.md        # This file
├── README.md                # Landing page
├── CONTRIBUTING.md
├── index.html               # Website
└── style.css
```

---

## Development Phases

### Phase 1: Foundation (CURRENT)
**Goal**: Get core Python orchestrator working on any Linux machine

- [ ] Create `src/aios/` directory structure
- [ ] Implement basic orchestrator (`src/aios/core.py`)
- [ ] Create configuration loader (`src/aios/config.py`)
- [ ] Set up CAMEL integration (`src/aios/agents/`)
- [ ] Create tool definitions (`src/aios/tools/`)
- [ ] Write basic CLI (`src/aios/cli.py`)
- [ ] Test with Ollama locally (before vLLM)

### Phase 2: Voice Integration
**Goal**: Add speech input/output

- [ ] Integrate Whisper.cpp server
- [ ] Integrate Pocket-TTS server
- [ ] Create voice loop (`src/aios/voice.py`)
- [ ] Test end-to-end voice conversation

### Phase 3: Messaging Integration
**Goal**: Connect Clawdbot as interface

- [ ] Fork/modify Clawdbot for local model
- [ ] Create bridge between Clawdbot and AIOS
- [ ] Test with WhatsApp/Telegram

### Phase 4: Memory Layer
**Goal**: Persistent context and RAG

- [ ] Integrate Memos API
- [ ] Add vector store (Qdrant)
- [ ] Implement memory backend for CAMEL

### Phase 5: ARM Image
**Goal**: Bootable image for ARM devices

- [ ] Set up Buildroot configuration
- [ ] Create s6-rc service definitions
- [ ] Package all components
- [ ] Build and test on Orange Pi 5

---

## Current Task: Phase 1 - Foundation

### What to build first

```
src/
└── aios/
    ├── __init__.py
    ├── __main__.py          # Entry point: python -m aios
    ├── core.py              # Main orchestrator class
    ├── config.py            # Configuration loading
    ├── cli.py               # Command-line interface
    ├── agents/
    │   ├── __init__.py
    │   ├── base.py          # Base agent class
    │   ├── system.py        # System management agent
    │   └── assistant.py     # Personal assistant agent
    ├── tools/
    │   ├── __init__.py
    │   ├── terminal.py      # Bash/terminal tools
    │   ├── files.py         # File operations
    │   └── system.py        # System info tools
    └── memory/
        ├── __init__.py
        └── simple.py        # Simple in-memory storage (before Memos)
```

### Dependencies for Phase 1

```
# requirements.txt
camel-ai[tools]>=0.2.0
pyyaml>=6.0
click>=8.0
rich>=13.0
httpx>=0.25.0
```

### Minimal working example target

```python
# After Phase 1, this should work:
from aios import AIOS

aios = AIOS(config_path="config.yaml")
response = aios.chat("What files are in the current directory?")
print(response)
# Output: "I found 5 files: README.md, setup.py, ..."
# (AI used terminal tool to run 'ls' command)
```

---

## Technical Decisions Made

### Model: GLM-4.6V-Flash
- **Why**: Only 9B model with Vision + Tools + Reasoning
- **Quantization**: Q4_K_M for 16GB devices, Q4_K_S for 8GB
- **Serving**: vLLM preferred over Ollama (better tool calling)

### Orchestration: CAMEL
- **Why**: Native multi-agent, MCP support, scales to 1M agents
- **Installation**: `pip install camel-ai[tools]`
- **Note**: Use vLLM backend, Ollama has tool calling issues

### Voice: Whisper.cpp + Pocket-TTS
- **STT**: Whisper.cpp with "small" model (~500MB)
- **TTS**: Pocket-TTS with "alba" voice (~150MB)
- **Both**: Run as HTTP servers, CPU-only

### Messaging: Clawdbot
- **Why**: Best multi-platform gateway, MIT licensed
- **Modification needed**: Replace cloud AI with local vLLM endpoint
- **Gateway**: WebSocket on port 18789

### Memory: Memos + Qdrant
- **Short-term**: In-memory conversation buffer
- **Long-term**: Memos (Go + SQLite)
- **Semantic**: Qdrant for RAG

### Init System: s6-rc
- **Why**: Faster than systemd, simpler, better for embedded
- **Alternative**: runit (similar)

### Kernel: Buildroot
- **Why**: Minimal, reproducible, good ARM support
- **Alternative**: Yocto (more complex)

---

## Code Snippets to Reuse

### CAMEL with local vLLM

```python
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from camel.agents import ChatAgent

model = ModelFactory.create(
    model_platform=ModelPlatformType.VLLM,
    model_type="glm-4.6v-flash",
    url="http://localhost:8000/v1",
)

agent = ChatAgent(
    system_message="You are a helpful assistant.",
    model=model,
)

response = agent.run("Hello!")
```

### Terminal tool with CAMEL

```python
from camel.toolkits import BaseToolkit
from camel.functions import OpenAIFunction
import subprocess

class TerminalToolkit(BaseToolkit):
    @OpenAIFunction
    def execute_command(self, command: str) -> str:
        """Execute a shell command and return the output.

        Args:
            command: The shell command to execute
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or result.stderr
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error: {str(e)}"
```

### Configuration schema

```yaml
# config.yaml
system:
  name: "AIOS"
  language: "en"

inference:
  backend: "ollama"  # or "vllm"
  model: "glm-4.6v-flash"
  url: "http://localhost:11434/v1"

agents:
  system:
    enabled: true
    tools: ["terminal", "files"]
  assistant:
    enabled: true
    tools: ["search", "notes"]

tools:
  terminal:
    allowed_commands: ["ls", "cat", "grep", "find", "ps"]
    blocked_commands: ["rm -rf", "dd"]
  files:
    allowed_paths: ["/home", "/tmp"]
    blocked_paths: ["/etc", "/boot"]
```

---

## Next Session Checklist

When resuming development:

1. **Read this file** to restore context
2. **Check current phase** and tasks
3. **Create next component** in order:
   - `src/aios/__init__.py`
   - `src/aios/config.py`
   - `src/aios/core.py`
   - etc.
4. **Test locally** with Ollama (easier than vLLM for dev)
5. **Update this file** with progress

---

## Commands Reference

```bash
# Clone repo
git clone https://github.com/raym33/ainative.git
cd ainative

# Install dev dependencies (once src/ exists)
pip install -e ".[dev]"

# Run AIOS (once implemented)
python -m aios

# Or with CLI
aios chat "Hello"
aios status
aios config show

# Run tests
pytest tests/

# Build image (Phase 5)
make image TARGET=orangepi5
```

---

## External Resources

- **CAMEL docs**: https://docs.camel-ai.org/
- **GLM-4.6V-Flash**: https://huggingface.co/zai-org/GLM-4.6V-Flash
- **Clawdbot**: https://github.com/clawdbot/clawdbot
- **Whisper.cpp**: https://github.com/ggerganov/whisper.cpp
- **Pocket-TTS**: https://github.com/kyutai-labs/pocket-tts
- **Memos**: https://github.com/usememos/memos
- **Buildroot**: https://buildroot.org/

---

## Session Log

### 2025-01-18 (Session 1)
- ✅ Discussed overall architecture
- ✅ Analyzed all component repos (Clawdbot, CAMEL, GLM, etc.)
- ✅ Designed layered architecture
- ✅ Created full documentation (13 files)
- ✅ Created FEATURES.md with installation guide
- ✅ Created this session context file
- 🔲 Next: Start implementing `src/aios/`

---

**End of session context. Ready to continue development.**
