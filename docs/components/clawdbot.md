# Clawdbot

Clawdbot serves as the unified messaging gateway for AI-Native OS, providing a single interface for all communication channels.

## Overview

| Attribute | Value |
|-----------|-------|
| Repository | [clawdbot/clawdbot](https://github.com/clawdbot/clawdbot) |
| Language | TypeScript |
| Runtime | Node.js ≥22 |
| License | MIT |
| Role | Interface Layer - Messaging Gateway |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Clawdbot                                 │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Gateway (WebSocket)                     │  │
│  │                  ws://127.0.0.1:18789                     │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────┬───────────┬───┴────┬──────────┬────────────────┐  │
│  │WhatsApp │ Telegram  │ Slack  │ Discord  │    Signal      │  │
│  │(Baileys)│ (grammY)  │ (Bolt) │(discord. │  (signal-cli)  │  │
│  │         │           │        │   js)    │                │  │
│  └─────────┴───────────┴────────┴──────────┴────────────────┘  │
│                                                                 │
│  ┌─────────┬───────────┬────────────────────────────────────┐  │
│  │iMessage │  Teams    │            WebChat                 │  │
│  │ (macOS) │(Bot Frmwk)│                                    │  │
│  └─────────┴───────────┴────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      Features                             │  │
│  │  • Skills system    • Canvas UI     • Browser control    │  │
│  │  • Cron jobs        • Docker sandbox • Voice (modified)  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Supported Channels

| Channel | Library | Status |
|---------|---------|--------|
| WhatsApp | Baileys | ✅ Stable |
| Telegram | grammY | ✅ Stable |
| Slack | Bolt | ✅ Stable |
| Discord | discord.js | ✅ Stable |
| Signal | signal-cli | ✅ Stable |
| iMessage | Native (macOS) | ⚠️ macOS only |
| Microsoft Teams | Bot Framework | ✅ Stable |
| WebChat | Built-in | ✅ Stable |

## Gateway Protocol

Clawdbot exposes a WebSocket API for internal communication.

**Connection:**
```javascript
const ws = new WebSocket('ws://127.0.0.1:18789');
```

**Message Format:**
```json
{
  "type": "message",
  "channel": "whatsapp",
  "user_id": "1234567890",
  "text": "Hello, AI",
  "attachments": [],
  "timestamp": 1705567890123
}
```

**Available Methods:**
- `node.list` - List connected devices
- `node.describe` - Get device capabilities
- `node.invoke` - Execute action on device
- `session.create` - Create new session
- `session.destroy` - End session
- `channel.send` - Send message to channel

## Modifications for AI-Native OS

### 1. Replace Cloud AI with Local Model

**Original (cloud):**
```typescript
const response = await anthropic.messages.create({
  model: "claude-3-opus",
  messages: [{ role: "user", content: userMessage }]
});
```

**Modified (local vLLM):**
```typescript
const response = await fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: "glm-4.6v-flash",
    messages: [{ role: "user", content: userMessage }]
  })
});
```

### 2. Replace ElevenLabs with Pocket-TTS

**Original:**
```typescript
const audio = await elevenlabs.generate({
  text: responseText,
  voice: "Rachel"
});
```

**Modified:**
```typescript
const audio = await fetch('http://localhost:8080/synthesize', {
  method: 'POST',
  body: JSON.stringify({ text: responseText, voice: "alba" })
});
```

### 3. Add Whisper.cpp for STT

```typescript
// New voice input handler
async function handleVoiceInput(audioBuffer: Buffer): Promise<string> {
  const result = await fetch('http://localhost:8081/transcribe', {
    method: 'POST',
    body: audioBuffer
  });
  return result.text;
}
```

## Configuration

**Location:** `~/.clawdbot/clawdbot.json`

```json
{
  "gateway": {
    "port": 18789,
    "host": "127.0.0.1"
  },
  "channels": {
    "whatsapp": {
      "enabled": true,
      "session_path": "~/.clawdbot/whatsapp"
    },
    "telegram": {
      "enabled": true,
      "bot_token": "YOUR_BOT_TOKEN"
    },
    "webchat": {
      "enabled": true,
      "port": 3000
    }
  },
  "ai": {
    "backend": "local",
    "endpoint": "http://localhost:8000/v1",
    "model": "glm-4.6v-flash"
  },
  "voice": {
    "tts_endpoint": "http://localhost:8080",
    "stt_endpoint": "http://localhost:8081"
  },
  "security": {
    "require_pairing": true,
    "sandbox_groups": true
  }
}
```

## Security Model

### DM Pairing
By default, unknown senders must pair via short code before interacting.

### Docker Sandboxing
Non-main sessions (groups, channels) run in isolated Docker containers.

### Permission Levels
```
main session     → Full host access
paired DM        → Limited tools
group/channel    → Sandboxed only
unknown          → Blocked
```

## Resource Usage

| Metric | Value |
|--------|-------|
| RAM | ~150MB |
| Storage | ~100MB |
| CPU (idle) | <1% |
| CPU (active) | 5-15% |

## Integration with CAMEL

Clawdbot forwards messages to CAMEL for processing:

```typescript
// clawdbot → camel bridge
gateway.on('message', async (msg) => {
  const response = await camelOrchestrator.process({
    text: msg.text,
    user_id: msg.user_id,
    channel: msg.channel,
    attachments: msg.attachments
  });

  await gateway.send(msg.channel, msg.user_id, response);
});
```

## Installation

```bash
# Global install
npm install -g clawdbot
clawdbot onboard --install-daemon

# Or from source
git clone https://github.com/clawdbot/clawdbot
cd clawdbot
pnpm install
pnpm build
```

## Related Documentation

- [Voice Stack](voice.md) - Whisper.cpp + Pocket-TTS integration
- [CAMEL](camel.md) - How messages are processed
- [Configuration Guide](../guides/configuration.md) - Full configuration reference
