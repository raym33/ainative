# System Architecture Overview

AI-Native OS is built as a layered architecture where each layer has a specific responsibility. The design prioritizes local-first operation, minimal resource usage, and AI as the primary interface.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                            AI-NATIVE OS v1.0                                │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│                           ┌─────────────────┐                               │
│                           │      USER       │                               │
│                           └────────┬────────┘                               │
│                                    │                                        │
│  ┌─────────────────────────────────┼─────────────────────────────────────┐  │
│  │                         INTERFACE LAYER                               │  │
│  │                                                                       │  │
│  │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │                    Clawdbot Gateway                          │    │  │
│  │   │                  ws://127.0.0.1:18789                        │    │  │
│  │   │                                                              │    │  │
│  │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐  │    │  │
│  │   │  │WhatsApp │ │Telegram │ │ Discord │ │ Signal  │ │ Web   │  │    │  │
│  │   │  │         │ │         │ │         │ │         │ │ Chat  │  │    │  │
│  │   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────┘  │    │  │
│  │   └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  │   ┌──────────────────────┐      ┌──────────────────────┐             │  │
│  │   │   Whisper.cpp        │      │    Pocket-TTS        │             │  │
│  │   │   (Speech-to-Text)   │ ←──→ │   (Text-to-Speech)   │             │  │
│  │   │   ~500MB             │      │   ~150MB             │             │  │
│  │   └──────────────────────┘      └──────────────────────┘             │  │
│  │                                                                       │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         ORCHESTRATION LAYER                           │  │
│  │                                                                       │  │
│  │   ┌───────────────────────────────────────────────────────────────┐  │  │
│  │   │                         CAMEL                                  │  │  │
│  │   │                   Multi-Agent Framework                        │  │  │
│  │   │                                                                │  │  │
│  │   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │  │  │
│  │   │  │   System    │ │  Assistant  │ │   Browser   │ │  Vision  │ │  │  │
│  │   │  │   Agent     │ │   Agent     │ │   Agent     │ │  Agent   │ │  │  │
│  │   │  │             │ │             │ │             │ │          │ │  │  │
│  │   │  │ • Services  │ │ • Chat      │ │ • Web nav   │ │ • Screen │ │  │  │
│  │   │  │ • Processes │ │ • Tasks     │ │ • Scraping  │ │ • Camera │ │  │  │
│  │   │  │ • Config    │ │ • Calendar  │ │ • Forms     │ │ • OCR    │ │  │  │
│  │   │  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │  │  │
│  │   │                                                                │  │  │
│  │   │  ┌─────────────────────────────────────────────────────────┐  │  │  │
│  │   │  │                    Societies                             │  │  │  │
│  │   │  │         (Role-Playing & Workforce coordination)          │  │  │  │
│  │   │  └─────────────────────────────────────────────────────────┘  │  │  │
│  │   │                                                                │  │  │
│  │   └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          INFERENCE LAYER                              │  │
│  │                                                                       │  │
│  │   ┌───────────────────────────────────────────────────────────────┐  │  │
│  │   │                   GLM-4.6V-Flash (9B)                          │  │  │
│  │   │                      via vLLM                                  │  │  │
│  │   │                                                                │  │  │
│  │   │   ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │  │  │
│  │   │   │   Vision    │ │   Tools     │ │      Reasoning          │ │  │  │
│  │   │   │   ✅        │ │   ✅        │ │      ✅                 │ │  │  │
│  │   │   │             │ │             │ │                         │ │  │  │
│  │   │   │ Screenshots │ │ Function    │ │ Planning, multi-step    │ │  │  │
│  │   │   │ Camera      │ │ Calling     │ │ <think> tags            │ │  │  │
│  │   │   │ Documents   │ │ Native      │ │                         │ │  │  │
│  │   │   └─────────────┘ └─────────────┘ └─────────────────────────┘ │  │  │
│  │   │                                                                │  │  │
│  │   │   Context: 128K tokens    RAM: ~6GB (Q4)    License: MIT      │  │  │
│  │   └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                           TOOLS LAYER                                 │  │
│  │                                                                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Terminal │ │  Files   │ │ Browser  │ │   Apps   │ │ Network  │   │  │
│  │  │          │ │          │ │          │ │          │ │          │   │  │
│  │  │ bash     │ │ read     │ │ navigate │ │ launch   │ │ http     │   │  │
│  │  │ systemctl│ │ write    │ │ click    │ │ close    │ │ dns      │   │  │
│  │  │ ps/kill  │ │ search   │ │ type     │ │ focus    │ │ ssh      │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  │                                                                       │  │
│  │  ┌──────────────────────────────────────────────────────────────┐    │  │
│  │  │                    MCP Protocol                               │    │  │
│  │  │         (Model Context Protocol - Anthropic standard)         │    │  │
│  │  └──────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          MEMORY LAYER                                 │  │
│  │                                                                       │  │
│  │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │                        Memos                                 │    │  │
│  │   │                   (Knowledge Base)                           │    │  │
│  │   │                                                              │    │  │
│  │   │  ┌────────────┐ ┌────────────┐ ┌────────────────────────┐   │    │  │
│  │   │  │ User Prefs │ │ Chat Logs  │ │ System Knowledge       │   │    │  │
│  │   │  │            │ │            │ │                        │   │    │  │
│  │   │  │ Settings   │ │ History    │ │ Learned behaviors      │   │    │  │
│  │   │  │ Habits     │ │ Context    │ │ Custom skills          │   │    │  │
│  │   │  └────────────┘ └────────────┘ └────────────────────────┘   │    │  │
│  │   │                                                              │    │  │
│  │   │   Backend: SQLite/PostgreSQL    API: REST + gRPC            │    │  │
│  │   └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │                   Vector Store (RAG)                         │    │  │
│  │   │                Qdrant / ChromaDB (embeddings)                │    │  │
│  │   └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          SYSTEM LAYER                                 │  │
│  │                                                                       │  │
│  │   ┌─────────────────────────────────────────────────────────────┐    │  │
│  │   │                   Linux Kernel (ARM64)                       │    │  │
│  │   │                     Buildroot / Yocto                        │    │  │
│  │   │                                                              │    │  │
│  │   │  ┌────────────┐ ┌────────────┐ ┌────────────────────────┐   │    │  │
│  │   │  │ Drivers    │ │ Networking │ │ Container Runtime      │   │    │  │
│  │   │  │            │ │            │ │                        │   │    │  │
│  │   │  │ GPU (Mali) │ │ WiFi/BT    │ │ Podman (rootless)      │   │    │  │
│  │   │  │ NPU        │ │ Ethernet   │ │ Sandbox for tools      │   │    │  │
│  │   │  │ Camera     │ │ TCP/IP     │ │                        │   │    │  │
│  │   │  └────────────┘ └────────────┘ └────────────────────────┘   │    │  │
│  │   │                                                              │    │  │
│  │   │   Init: systemd-free (s6/runit)    Libc: musl              │    │  │
│  │   └─────────────────────────────────────────────────────────────┘    │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. AI-First Interface
The primary way to interact with the OS is through natural language (voice or text). Traditional GUI is secondary.

### 2. Local-First
All AI inference happens on-device. No cloud dependencies for core functionality. User data never leaves the device.

### 3. Single Model Architecture
Instead of routing between multiple specialized models, we use GLM-4.6V-Flash which combines:
- **Vision** - Understanding screenshots, camera, documents
- **Tool Use** - Native function calling
- **Reasoning** - Multi-step planning with `<think>` tags

This eliminates model-swapping latency and context fragmentation.

### 4. Unified Messaging
Clawdbot provides a single inbox for all communication platforms. Whether you message via WhatsApp, Telegram, or voice, the experience is consistent.

### 5. Persistent Memory
Memos serves as the system's long-term memory, storing:
- User preferences and habits
- Conversation history
- Learned behaviors and custom skills

### 6. Sandboxed Execution
All tool execution happens in Podman containers, providing security isolation without the overhead of full VMs.

## Layer Responsibilities

| Layer | Primary Component | Responsibility |
|-------|------------------|----------------|
| Interface | Clawdbot + Voice | User input/output across all channels |
| Orchestration | CAMEL | Multi-agent coordination and task routing |
| Inference | GLM-4.6V-Flash | Understanding, reasoning, decision making |
| Tools | MCP Toolkit | Executing actions on the system |
| Memory | Memos + Qdrant | Persistent context and knowledge retrieval |
| System | Linux ARM64 | Hardware abstraction and resource management |

## Why This Stack?

### GLM-4.6V-Flash over alternatives
- Only 9B model with native Vision + Tools + Reasoning
- 128K context window
- MIT licensed
- Optimized for local deployment

### CAMEL over LangChain/AutoGen
- Native multi-agent societies
- Scales to 1M agents
- MCP protocol support
- Lighter footprint

### Clawdbot over custom interface
- Battle-tested multi-platform support
- WebSocket gateway architecture
- Active development (6,500+ commits)

### Memos over custom storage
- Privacy-first design
- REST + gRPC APIs
- Lightweight (Go + SQLite)

## Next Steps

- [Data Flow](data-flow.md) - How requests move through the system
- [Component Stack](stack.md) - Detailed resource requirements
- [Hardware Guide](../guides/hardware.md) - Supported devices
