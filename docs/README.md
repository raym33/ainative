# AI-Native OS Documentation

Welcome to the AI-Native OS documentation. This project aims to build a minimal, AI-first operating system for ARM chips that combines the best open-source AI projects into a cohesive, local-first experience.

## Overview

AI-Native OS is designed around a simple principle: **AI should be the primary interface**, not an afterthought. Instead of adding AI capabilities to a traditional OS, we're building an OS where AI orchestration is the core.

## Documentation Structure

### Architecture
- [System Overview](architecture/overview.md) - High-level architecture and design principles
- [Data Flow](architecture/data-flow.md) - How data moves through the system
- [Component Stack](architecture/stack.md) - Full component breakdown with resource requirements

### Components
- [Clawdbot](components/clawdbot.md) - Multi-platform messaging gateway
- [CAMEL](components/camel.md) - Multi-agent orchestration framework
- [GLM-4.6V-Flash](components/glm-model.md) - Vision + Tools + Reasoning model
- [Voice Stack](components/voice.md) - Whisper.cpp + Pocket-TTS
- [Memos](components/memos.md) - Knowledge base and memory system

### Guides
- [Hardware Requirements](guides/hardware.md) - Supported devices and recommendations
- [Configuration](guides/configuration.md) - System configuration reference
- [Boot Sequence](guides/boot-sequence.md) - Init process and service startup
- [Building from Source](guides/building.md) - How to build the OS image

## Quick Links

| Resource | Description |
|----------|-------------|
| [Architecture Overview](architecture/overview.md) | Start here for the big picture |
| [Hardware Guide](guides/hardware.md) | What hardware you need |
| [Configuration](guides/configuration.md) | How to configure the system |

## Project Repositories

This OS integrates several amazing open-source projects:

| Project | Role | Repository |
|---------|------|------------|
| Clawdbot | Messaging Gateway | [clawdbot/clawdbot](https://github.com/clawdbot/clawdbot) |
| CAMEL | Agent Orchestration | [camel-ai/camel](https://github.com/camel-ai/camel) |
| GLM-4.6V-Flash | Core AI Model | [zai-org/GLM-4.6V-Flash](https://huggingface.co/zai-org/GLM-4.6V-Flash) |
| Pocket-TTS | Text-to-Speech | [kyutai-labs/pocket-tts](https://github.com/kyutai-labs/pocket-tts) |
| Whisper.cpp | Speech-to-Text | [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp) |
| Memos | Knowledge Base | [usememos/memos](https://github.com/usememos/memos) |
| vLLM | Model Serving | [vllm-project/vllm](https://github.com/vllm-project/vllm) |

## License

MIT License - See [LICENSE](../LICENSE) for details.
