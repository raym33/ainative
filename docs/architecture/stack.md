# Component Stack

Complete breakdown of all components with resource requirements and alternatives.

## Resource Summary

| Layer | Component | Function | RAM | Storage |
|-------|-----------|----------|-----|---------|
| **Interface** | Clawdbot | Messaging gateway | ~150MB | ~100MB |
| | Whisper.cpp | Speech-to-Text | ~500MB | ~500MB |
| | Pocket-TTS | Text-to-Speech | ~150MB | ~100MB |
| **Orchestration** | CAMEL | Multi-agent framework | ~150MB | ~50MB |
| **Inference** | vLLM | Model server | ~200MB | ~50MB |
| | GLM-4.6V-Flash | Core AI model | ~6GB | ~6GB |
| **Tools** | MCP Toolkit | Tool execution | ~50MB | ~20MB |
| **Memory** | Memos | Knowledge base | ~50MB | variable |
| | Qdrant | Vector store | ~100MB | variable |
| **System** | Linux ARM64 | Kernel + base | ~100MB | ~200MB |
| | Podman | Container runtime | ~50MB | ~100MB |
| **TOTAL** | | | **~7.5GB** | **~7GB** |

## Detailed Component Analysis

### Interface Layer

#### Clawdbot
**Role**: Unified messaging gateway

| Attribute | Value |
|-----------|-------|
| Repository | [clawdbot/clawdbot](https://github.com/clawdbot/clawdbot) |
| Language | TypeScript |
| Runtime | Node.js ≥22 |
| License | MIT |
| Stars | 5,000+ |

**Supported Channels:**
- WhatsApp (via Baileys)
- Telegram (via grammY)
- Slack (via Bolt)
- Discord (via discord.js)
- Signal (via signal-cli)
- iMessage (macOS only)
- Microsoft Teams
- WebChat

**Key Features:**
- WebSocket gateway (ws://127.0.0.1:18789)
- Docker sandbox for untrusted sessions
- Skills/workflow automation
- DM pairing for security

**Modifications Needed for AI-Native OS:**
- Replace cloud model APIs with local vLLM endpoint
- Replace ElevenLabs with Pocket-TTS
- Add Whisper.cpp integration for voice

---

#### Whisper.cpp
**Role**: Local speech-to-text

| Attribute | Value |
|-----------|-------|
| Repository | [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp) |
| Language | C++ |
| License | MIT |
| Stars | 35,000+ |

**Models:**

| Model | Size | RAM | Quality |
|-------|------|-----|---------|
| tiny | 75MB | ~200MB | Basic |
| small | 500MB | ~500MB | Good |
| medium | 1.5GB | ~1.5GB | Better |
| large | 3GB | ~3GB | Best |

**Recommendation**: Use `small` model for balance of quality and resources.

---

#### Pocket-TTS
**Role**: Local text-to-speech

| Attribute | Value |
|-----------|-------|
| Repository | [kyutai-labs/pocket-tts](https://github.com/kyutai-labs/pocket-tts) |
| Language | Python (PyTorch) |
| License | Apache 2.0 |

**Key Features:**
- CPU-only operation (no GPU required)
- ~200ms latency to first audio
- 6x faster than real-time on Apple Silicon
- 8 built-in voices
- Voice cloning support

**Voices**: Alba, Marius, Javert, Jean, Fantine, Cosette, Eponine, Azelma

---

### Orchestration Layer

#### CAMEL
**Role**: Multi-agent coordination

| Attribute | Value |
|-----------|-------|
| Repository | [camel-ai/camel](https://github.com/camel-ai/camel) |
| Language | Python |
| License | Apache 2.0 |
| Stars | 15,600+ |

**Module Structure:**
```
camel/
├── agents/          # ChatAgent, TaskAgent, etc.
├── societies/       # Role-playing, Workforce
├── models/          # OpenAI, Ollama, vLLM backends
├── memories/        # Chat history, vector memory
├── toolkits/        # Browser, terminal, files
├── retrievers/      # RAG components
├── interpreters/    # Code execution
└── embeddings/      # Vector generation
```

**Installation Options:**
```bash
pip install camel-ai           # Core (~50MB)
pip install 'camel-ai[tools]'  # + toolkits (~70MB)
pip install 'camel-ai[rag]'    # + RAG (~150MB)
pip install 'camel-ai[all]'    # Everything (~300MB)
```

**Local Model Support:**
```python
from camel.models import ModelFactory
from camel.types import ModelPlatformType

model = ModelFactory.create(
    model_platform=ModelPlatformType.VLLM,
    model_type="glm-4.6v-flash",
    url="http://localhost:8000/v1",
)
```

**Key Features:**
- Scales to 1M agents
- MCP protocol support
- Memory persistence
- Role-playing societies
- Workforce coordination

---

### Inference Layer

#### GLM-4.6V-Flash
**Role**: Core AI model (Vision + Tools + Reasoning)

| Attribute | Value |
|-----------|-------|
| Model | [zai-org/GLM-4.6V-Flash](https://huggingface.co/zai-org/GLM-4.6V-Flash) |
| Parameters | 9B (10B actual) |
| Context | 128K tokens |
| License | MIT |

**Capabilities:**

| Feature | Status | Notes |
|---------|--------|-------|
| Vision | ✅ Native | Screenshots, camera, documents |
| Tool Use | ✅ Native | Function calling without prompting |
| Reasoning | ✅ Partial | `<think>` tags for chain-of-thought |

**Quantization Options:**

| Quantization | VRAM | System RAM | Quality |
|--------------|------|------------|---------|
| BF16 | ~20GB | ~24GB | Best |
| Q8 | ~10GB | ~14GB | Excellent |
| Q4_K_M | ~6GB | ~8GB | Good |
| Q4_K_S | ~5GB | ~7GB | Acceptable |

**Why GLM-4.6V-Flash over alternatives:**

| Model | Params | Vision | Tools | Reasoning | Context |
|-------|--------|--------|-------|-----------|---------|
| **GLM-4.6V-Flash** | 9B | ✅ | ✅ | ✅ | 128K |
| Qwen2-VL | 7B | ✅ | ✅ | ❌ | 32K |
| Phi-3.5-Vision | 4B | ✅ | ⚠️ | ❌ | 128K |
| Llama 3.2 Vision | 11B | ✅ | ❌ | ❌ | 128K |
| DeepSeek-R1 | 7B | ❌ | ✅ | ✅ | 32K |

GLM-4.6V-Flash is the only ~9B model with all three capabilities.

---

#### vLLM
**Role**: High-performance model serving

| Attribute | Value |
|-----------|-------|
| Repository | [vllm-project/vllm](https://github.com/vllm-project/vllm) |
| Language | Python/C++ |
| License | Apache 2.0 |

**Why vLLM over Ollama:**
- Better tool calling support
- Higher throughput (PagedAttention)
- Better ARM64 support
- OpenAI-compatible API

---

### Memory Layer

#### Memos
**Role**: Knowledge base and persistent memory

| Attribute | Value |
|-----------|-------|
| Repository | [usememos/memos](https://github.com/usememos/memos) |
| Language | Go + React |
| License | MIT |
| Stars | 35,000+ |

**Key Features:**
- Privacy-first (zero telemetry)
- SQLite/PostgreSQL backend
- REST + gRPC APIs
- Markdown support
- Full data export

**Use Cases in AI-Native OS:**
- User preferences storage
- Conversation history
- Learned behaviors
- Custom skills/workflows

---

#### Qdrant
**Role**: Vector database for RAG

| Attribute | Value |
|-----------|-------|
| Repository | [qdrant/qdrant](https://github.com/qdrant/qdrant) |
| Language | Rust |
| License | Apache 2.0 |

**Alternatives:** ChromaDB (simpler), Milvus (enterprise)

---

### System Layer

#### Linux Kernel
**Build System**: Buildroot or Yocto

**Target Configuration:**
- Kernel: 6.x LTS
- Libc: musl (smaller than glibc)
- Init: s6 or runit (no systemd)
- Shell: busybox

**Required Drivers:**
- GPU: Mali (for ARM GPUs)
- NPU: Board-specific
- WiFi/Bluetooth
- Camera (V4L2)
- Audio (ALSA)

---

#### Podman
**Role**: Rootless container runtime

Used for sandboxing tool execution. Lighter than Docker, no daemon required.

```bash
# Example: Execute command in sandbox
podman run --rm -it --security-opt=no-new-privileges \
  aios-sandbox bash -c "curl example.com"
```

---

## Alternative Configurations

### Minimal (RPi 5 8GB)
```
Whisper (tiny)        ~200MB
Pocket-TTS            ~150MB
GLM-4.6V-Flash (Q4)   ~5GB
CAMEL (core)          ~100MB
Memos                 ~50MB
Linux                 ~100MB
─────────────────────────────
Total:                ~5.6GB  (leaves ~2GB for OS)
```

### Recommended (16GB device)
```
Whisper (small)       ~500MB
Pocket-TTS            ~150MB
GLM-4.6V-Flash (Q4)   ~6GB
CAMEL (full)          ~200MB
Memos + Qdrant        ~150MB
Clawdbot              ~150MB
Linux + Podman        ~200MB
─────────────────────────────
Total:                ~7.4GB  (leaves ~8GB headroom)
```

### Optimal (32GB device)
```
Whisper (medium)      ~1.5GB
Pocket-TTS + VoxCPM   ~500MB
GLM-4.6V-Flash (Q8)   ~10GB
CAMEL (all)           ~300MB
Memos + Qdrant        ~500MB
Clawdbot              ~200MB
Linux + Podman        ~300MB
Browser (WebKitGTK)   ~500MB
─────────────────────────────
Total:                ~13.8GB (leaves ~18GB headroom)
```
