# Boot Sequence

This guide documents the complete boot sequence for AI-Native OS, from kernel init to "AI ready" state.

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      BOOT SEQUENCE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. [0.0s]  Linux kernel init                              │
│                                                             │
│  2. [0.5s]  Mount filesystems                              │
│                                                             │
│  3. [1.0s]  Start core services (s6-rc)                    │
│             ├── networking                                  │
│             ├── dbus                                        │
│             └── podman socket                               │
│                                                             │
│  4. [2.0s]  Start AI services                              │
│             ├── memos (memory)                              │
│             ├── vllm (model server)      ← ~30s warm-up    │
│             ├── whisper (STT daemon)                        │
│             └── pocket-tts (TTS daemon)                     │
│                                                             │
│  5. [35s]   Start interface layer                          │
│             ├── clawdbot gateway                            │
│             └── camel orchestrator                          │
│                                                             │
│  6. [40s]   READY STATE                                    │
│             └── "AI OS ready" (spoken via Pocket-TTS)      │
│                                                             │
│  7. [40s+]  Listening for input...                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Phases

### Phase 1: Kernel Init (0-1s)

The Linux kernel initializes hardware and mounts the root filesystem.

**Key events:**
- CPU initialization
- Memory detection
- Device enumeration
- Root filesystem mount

**Configuration:** Kernel command line in `/boot/cmdline.txt`

```
root=/dev/mmcblk0p2 rootfstype=ext4 quiet loglevel=3
```

### Phase 2: Filesystem Mount (0.5-1s)

Mount additional filesystems.

**Mounts:**
```
/boot       - Boot partition (FAT32)
/var        - Variable data
/home       - User data
/tmp        - Temporary (tmpfs)
```

**Configuration:** `/etc/fstab`

```
/dev/mmcblk0p1  /boot   vfat    defaults        0 2
/dev/mmcblk0p2  /       ext4    defaults,noatime 0 1
tmpfs           /tmp    tmpfs   defaults,size=256M 0 0
```

### Phase 3: Core Services (1-2s)

The init system (s6-rc) starts essential services.

**Services started:**
1. **networking** - Network interfaces and DHCP
2. **dbus** - Message bus for IPC
3. **podman** - Container socket for sandboxing
4. **syslog** - System logging

**Configuration:** `/etc/s6-rc/`

```
/etc/s6-rc/
├── source/
│   ├── networking/
│   │   ├── type (oneshot)
│   │   └── up
│   ├── dbus/
│   │   ├── type (longrun)
│   │   └── run
│   └── podman/
│       ├── type (longrun)
│       └── run
└── compiled/
```

### Phase 4: AI Services (2-35s)

Start AI-specific services. This is the longest phase due to model loading.

#### 4.1 Memos (2-3s)

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/memos/run

fdmove -c 2 1
/opt/memos/memos
  --mode prod
  --port 5230
  --data /var/aios/memos
```

#### 4.2 vLLM Model Server (3-35s)

This is the slowest component - loading the model into memory.

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/vllm/run

fdmove -c 2 1
cd /opt/vllm
/usr/bin/python -m vllm.entrypoints.openai.api_server
  --model /var/aios/models/glm-4.6v-flash
  --quantization awq
  --max-model-len 32768
  --host 127.0.0.1
  --port 8000
```

**Optimization tips:**
- Use faster storage (NVMe > SD card)
- Pre-warm model cache
- Use smaller quantization for faster load

#### 4.3 Whisper STT (3-5s)

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/whisper/run

fdmove -c 2 1
/opt/whisper/server
  -m /var/aios/models/whisper/ggml-small.bin
  --host 127.0.0.1
  --port 8081
```

#### 4.4 Pocket-TTS (3-5s)

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/pocket-tts/run

fdmove -c 2 1
cd /opt/pocket-tts
/usr/bin/python -m pocket_tts.server
  --host 127.0.0.1
  --port 8080
```

### Phase 5: Interface Layer (35-40s)

Start user-facing services after AI backend is ready.

#### 5.1 Wait for vLLM

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/wait-vllm/up

# Wait for vLLM to be healthy
foreground {
  /usr/bin/timeout 120
  /usr/bin/sh -c "until curl -s http://localhost:8000/health; do sleep 1; done"
}
```

#### 5.2 Clawdbot Gateway

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/clawdbot/run

fdmove -c 2 1
cd /opt/clawdbot
/usr/bin/node dist/index.js
```

**Dependencies:**
```
# /etc/s6-rc/source/clawdbot/dependencies
vllm
memos
whisper
pocket-tts
```

#### 5.3 CAMEL Orchestrator

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/camel/run

fdmove -c 2 1
cd /opt/camel
/usr/bin/python -m aios.orchestrator
```

### Phase 6: Ready State (40s)

All services are running. Announce ready state.

```bash
#!/bin/execlineb -P
# /etc/s6-rc/source/ready/up

# Announce via TTS
foreground {
  curl -X POST http://localhost:8080/synthesize
    -H "Content-Type: application/json"
    -d '{"text": "AI OS ready. How can I help you?", "voice": "alba"}'
    | aplay -
}

# Log ready state
foreground {
  echo "AIOS ready at $(date)" >> /var/log/aios/boot.log
}

# Create ready marker
touch /run/aios-ready
```

## Service Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                   Dependency Graph                          │
│                                                             │
│   networking                                                │
│       │                                                     │
│       ├──→ memos                                            │
│       │                                                     │
│       ├──→ vllm ────────────────┐                          │
│       │                         │                          │
│       ├──→ whisper ─────────────┼──→ clawdbot ──→ ready   │
│       │                         │        │                  │
│       └──→ pocket-tts ──────────┘        │                  │
│                                          │                  │
│                                    camel ┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Boot Time Optimization

### Current (baseline)

| Phase | Time | Cumulative |
|-------|------|------------|
| Kernel | 1s | 1s |
| Filesystems | 0.5s | 1.5s |
| Core services | 1s | 2.5s |
| Memos | 1s | 3.5s |
| vLLM load | 30s | 33.5s |
| Whisper | 2s | 35.5s |
| Pocket-TTS | 2s | 37.5s |
| Clawdbot | 2s | 39.5s |
| Ready | 0.5s | **40s** |

### Optimized (parallel + NVMe)

| Phase | Time | Cumulative |
|-------|------|------------|
| Kernel | 1s | 1s |
| Filesystems | 0.5s | 1.5s |
| Core services | 1s | 2.5s |
| AI services (parallel) | 20s | 22.5s |
| Interface | 2s | 24.5s |
| Ready | 0.5s | **25s** |

**Optimizations applied:**
1. NVMe storage instead of SD card
2. Parallel service startup where possible
3. Model pre-cached in RAM (suspend/resume)

### Minimal Boot (voice-only)

If you only need voice interface:

| Phase | Time | Cumulative |
|-------|------|------------|
| Kernel | 1s | 1s |
| vLLM load | 20s | 21s |
| Whisper + TTS | 3s | 24s |
| Voice loop | 1s | **25s** |

## Monitoring Boot

### Boot log

```bash
# View boot log
cat /var/log/aios/boot.log

# Sample output:
# [0.00] AIOS boot started
# [1.52] Core services ready
# [3.21] Memos ready
# [32.45] vLLM ready (model loaded)
# [34.12] Whisper ready
# [35.89] Pocket-TTS ready
# [38.34] Clawdbot ready
# [39.01] CAMEL ready
# [39.56] AIOS ready
```

### Service status

```bash
# Check all services
s6-rc -a list

# Check specific service
s6-svstat /run/service/vllm

# View service logs
s6-log /var/log/aios/vllm/current
```

### Health endpoint

```bash
# System health
curl http://localhost:9090/health

# Response:
{
  "status": "healthy",
  "uptime": 3600,
  "services": {
    "vllm": "running",
    "whisper": "running",
    "pocket-tts": "running",
    "clawdbot": "running",
    "memos": "running"
  }
}
```

## Troubleshooting

### vLLM won't start

```bash
# Check memory
free -h

# Check logs
cat /var/log/aios/vllm/current

# Common issues:
# - Not enough RAM → Use smaller quantization
# - CUDA error → Check GPU drivers
# - Model not found → Verify model path
```

### Boot hangs at "waiting for vLLM"

```bash
# Check if vLLM is loading
curl http://localhost:8000/health

# Force timeout and continue
touch /run/aios-vllm-skip

# Boot without vLLM (limited functionality)
```

### Services crash on startup

```bash
# Check dependency order
s6-rc-db dependencies servicename

# View crash logs
s6-log /var/log/aios/servicename/current

# Restart single service
s6-svc -r /run/service/servicename
```

## Related Documentation

- [Configuration](configuration.md) - Service configuration
- [Hardware Guide](hardware.md) - Hardware-specific boot settings
- [Architecture Overview](../architecture/overview.md) - System design
