# Configuration Guide

This guide covers all configuration options for AI-Native OS.

## Configuration Files

| File | Purpose |
|------|---------|
| `/etc/aios/config.yaml` | Main system configuration |
| `/etc/aios/agents/*.yaml` | CAMEL agent definitions |
| `/etc/aios/tools/*.json` | MCP tool configurations |
| `~/.clawdbot/clawdbot.json` | Clawdbot messaging config |
| `/etc/aios/memos.env` | Memos environment |

## Main Configuration

**Location**: `/etc/aios/config.yaml`

```yaml
# AI-Native OS Configuration
# Version: 1.0.0

#
# SYSTEM
#
system:
  name: "AIOS"
  version: "1.0.0"
  language: "en"  # en, es, zh, etc.
  timezone: "UTC"
  log_level: "info"  # debug, info, warn, error
  log_path: "/var/log/aios"

#
# INFERENCE
#
inference:
  # Backend: vllm (recommended) or ollama
  backend: "vllm"

  # Model configuration
  model:
    name: "glm-4.6v-flash"
    path: "/var/aios/models/glm-4.6v-flash"
    quantization: "Q4_K_M"  # BF16, Q8, Q4_K_M, Q4_K_S

  # Server settings
  server:
    host: "127.0.0.1"
    port: 8000
    max_model_len: 32768  # Context length to use (max 128K)
    gpu_memory_utilization: 0.9

  # Generation defaults
  generation:
    temperature: 0.8
    top_p: 0.6
    top_k: 2
    repetition_penalty: 1.1
    max_tokens: 4096

#
# VOICE
#
voice:
  # Speech-to-Text (Whisper.cpp)
  stt:
    enabled: true
    engine: "whisper.cpp"
    model: "small"  # tiny, small, medium, large
    model_path: "/var/aios/models/whisper"
    server:
      host: "127.0.0.1"
      port: 8081
    language: "auto"  # auto, en, es, etc.
    beam_size: 5

  # Text-to-Speech (Pocket-TTS)
  tts:
    enabled: true
    engine: "pocket-tts"
    model_path: "/var/aios/models/pocket-tts"
    server:
      host: "127.0.0.1"
      port: 8080
    voice: "alba"  # alba, marius, javert, jean, fantine, cosette, eponine, azelma
    speed: 1.0
    sample_rate: 24000

  # Wake word (optional)
  wake_word:
    enabled: false
    phrase: "hey ai"
    sensitivity: 0.5

#
# INTERFACE
#
interface:
  # Clawdbot messaging gateway
  clawdbot:
    enabled: true
    gateway:
      host: "127.0.0.1"
      port: 18789

    # Enabled channels
    channels:
      whatsapp:
        enabled: true
        session_path: "~/.clawdbot/whatsapp"
      telegram:
        enabled: false
        bot_token: ""  # Set via environment variable
      discord:
        enabled: false
        bot_token: ""
      signal:
        enabled: false
      webchat:
        enabled: true
        port: 3000

    # Security
    security:
      require_pairing: true
      sandbox_groups: true
      allowed_users: []  # Empty = allow all paired users

#
# ORCHESTRATION
#
orchestration:
  framework: "camel"

  # Agent definitions
  agents:
    system:
      enabled: true
      config: "/etc/aios/agents/system.yaml"
    assistant:
      enabled: true
      config: "/etc/aios/agents/assistant.yaml"
    browser:
      enabled: true
      config: "/etc/aios/agents/browser.yaml"
    vision:
      enabled: true
      config: "/etc/aios/agents/vision.yaml"

  # Societies (multi-agent)
  societies:
    enabled: false
    max_agents: 5

#
# MEMORY
#
memory:
  # Memos (knowledge base)
  memos:
    enabled: true
    host: "127.0.0.1"
    port: 5230
    data_path: "/var/aios/memos"
    database: "sqlite"  # sqlite, postgres, mysql

  # Vector store (RAG)
  vectors:
    enabled: true
    engine: "qdrant"  # qdrant, chroma
    path: "/var/aios/vectors"
    embedding_model: "all-MiniLM-L6-v2"
    collection_name: "aios_memory"

  # Context settings
  context:
    max_history: 20  # Conversation turns to keep
    max_rag_results: 5

#
# TOOLS
#
tools:
  # MCP Protocol tools
  mcp:
    enabled: true
    config_path: "/etc/aios/tools/mcp.json"

  # Built-in toolkits
  toolkits:
    terminal:
      enabled: true
      allowed_commands: ["ls", "cat", "grep", "find", "ps", "systemctl"]
      blocked_commands: ["rm -rf", "dd", "mkfs"]
    files:
      enabled: true
      allowed_paths: ["/home", "/var/aios", "/tmp"]
      blocked_paths: ["/etc", "/boot", "/root"]
    browser:
      enabled: true
      headless: true
    network:
      enabled: true
      allowed_hosts: ["*"]
      blocked_hosts: []

#
# SECURITY
#
security:
  # Sandbox for tool execution
  sandbox:
    enabled: true
    runtime: "podman"  # podman, docker
    image: "aios-sandbox:latest"
    timeout: 30  # seconds
    memory_limit: "512m"
    network: "none"  # none, bridge, host

  # Actions requiring confirmation
  require_confirmation:
    - "rm"
    - "shutdown"
    - "reboot"
    - "systemctl stop"
    - "kill"

  # Rate limiting
  rate_limit:
    enabled: true
    requests_per_minute: 60

#
# MONITORING
#
monitoring:
  # Health checks
  health:
    enabled: true
    endpoint: "/health"
    port: 9090

  # Metrics (Prometheus)
  metrics:
    enabled: false
    endpoint: "/metrics"
    port: 9091

  # System stats
  stats:
    enabled: true
    interval: 60  # seconds
    log_path: "/var/log/aios/stats"
```

## Agent Configuration

### System Agent

**Location**: `/etc/aios/agents/system.yaml`

```yaml
name: system
description: "System management agent"
enabled: true

system_prompt: |
  You are the System Agent for AI-Native OS.

  Your responsibilities:
  - Manage system services (start, stop, restart)
  - Monitor system resources (CPU, RAM, disk)
  - Handle system configuration
  - Manage processes

  Rules:
  - Always confirm destructive actions with the user
  - Never execute commands that could brick the system
  - Log all system changes

tools:
  - terminal
  - files

permissions:
  terminal:
    allowed:
      - systemctl
      - ps
      - top
      - df
      - free
    blocked:
      - rm -rf /
      - dd
      - mkfs
```

### Assistant Agent

**Location**: `/etc/aios/agents/assistant.yaml`

```yaml
name: assistant
description: "Personal assistant agent"
enabled: true

system_prompt: |
  You are a helpful personal assistant.

  Your responsibilities:
  - Answer questions
  - Help with tasks
  - Manage reminders and notes
  - Provide information

  Personality:
  - Friendly but concise
  - Proactive but not intrusive
  - Respect user privacy

tools:
  - search
  - notes
  - calendar

permissions:
  search:
    max_results: 10
  notes:
    storage: memos
```

### Browser Agent

**Location**: `/etc/aios/agents/browser.yaml`

```yaml
name: browser
description: "Web automation agent"
enabled: true

system_prompt: |
  You are a Browser Agent.

  Your responsibilities:
  - Navigate websites
  - Fill forms
  - Extract information
  - Take screenshots

  Rules:
  - Never enter payment information
  - Ask before submitting forms
  - Respect robots.txt

tools:
  - browser

permissions:
  browser:
    headless: true
    timeout: 30
    blocked_domains:
      - "*.bank.*"
      - "*.gov"
```

### Vision Agent

**Location**: `/etc/aios/agents/vision.yaml`

```yaml
name: vision
description: "Visual understanding agent"
enabled: true

system_prompt: |
  You are a Vision Agent.

  Your responsibilities:
  - Analyze screenshots
  - Process camera input
  - Read documents (OCR)
  - Describe images

  Rules:
  - Be accurate in descriptions
  - Note any uncertainty
  - Respect privacy (blur faces if needed)

tools:
  - screenshot
  - camera
  - ocr

permissions:
  screenshot:
    max_frequency: 1  # per second
  camera:
    resolution: "720p"
```

## MCP Tools Configuration

**Location**: `/etc/aios/tools/mcp.json`

```json
{
  "version": "1.0",
  "tools": [
    {
      "name": "web_search",
      "description": "Search the web for information",
      "endpoint": "https://api.search.com/v1/search",
      "auth": {
        "type": "api_key",
        "header": "X-API-Key",
        "env_var": "SEARCH_API_KEY"
      }
    },
    {
      "name": "weather",
      "description": "Get weather information",
      "endpoint": "https://api.weather.com/v1/current",
      "auth": {
        "type": "api_key",
        "query_param": "apikey",
        "env_var": "WEATHER_API_KEY"
      }
    },
    {
      "name": "calendar",
      "description": "Manage calendar events",
      "endpoint": "local://calendar",
      "backend": "caldav",
      "config": {
        "server": "http://localhost:5232",
        "calendar": "default"
      }
    }
  ]
}
```

## Environment Variables

Create `/etc/aios/environment`:

```bash
# API Keys (optional, for external services)
SEARCH_API_KEY=your-search-api-key
WEATHER_API_KEY=your-weather-api-key

# Clawdbot tokens
TELEGRAM_BOT_TOKEN=your-telegram-token
DISCORD_BOT_TOKEN=your-discord-token

# Memos
MEMOS_TOKEN=your-memos-access-token

# Model paths (override config)
AIOS_MODEL_PATH=/var/aios/models/glm-4.6v-flash
WHISPER_MODEL_PATH=/var/aios/models/whisper/ggml-small.bin
```

## Clawdbot Configuration

**Location**: `~/.clawdbot/clawdbot.json`

```json
{
  "gateway": {
    "port": 18789,
    "host": "127.0.0.1"
  },
  "workspace": "~/clawd",
  "ai": {
    "backend": "local",
    "endpoint": "http://localhost:8000/v1",
    "model": "glm-4.6v-flash"
  },
  "voice": {
    "tts": {
      "endpoint": "http://localhost:8080",
      "voice": "alba"
    },
    "stt": {
      "endpoint": "http://localhost:8081"
    }
  },
  "channels": {
    "whatsapp": {
      "enabled": true
    },
    "webchat": {
      "enabled": true,
      "port": 3000
    }
  },
  "security": {
    "requirePairing": true,
    "sandboxGroups": true
  }
}
```

## Validation

Check configuration validity:

```bash
# Validate main config
aios config validate

# Check specific component
aios config check inference
aios config check voice
aios config check agents

# Show effective configuration
aios config show
```

## Hot Reload

Some settings can be reloaded without restart:

```bash
# Reload agent configs
aios reload agents

# Reload tool configs
aios reload tools

# Full reload (except kernel services)
aios reload all
```

## Related Documentation

- [Boot Sequence](boot-sequence.md) - How configuration is loaded at boot
- [Hardware Guide](hardware.md) - Hardware-specific configuration
- [Architecture Overview](../architecture/overview.md) - System design context
