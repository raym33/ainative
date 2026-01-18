# Hardware Guide

This guide covers supported hardware, requirements, and recommendations for running AI-Native OS.

## Minimum Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | ARM64 (ARMv8-A) | ARM64 with 4+ cores |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 32GB | 128GB+ NVMe |
| **GPU** | None (CPU inference) | Mali/Adreno or dedicated |

## Supported Devices

### Tier 1: Recommended

These devices are fully tested and provide the best experience.

#### Orange Pi 5 (16GB)

| Spec | Value |
|------|-------|
| SoC | Rockchip RK3588S |
| CPU | 4x Cortex-A76 + 4x Cortex-A55 |
| RAM | 16GB LPDDR4X |
| NPU | 6 TOPS |
| GPU | Mali-G610 MP4 |
| Storage | M.2 NVMe slot |
| Price | ~$150 |

**Performance:**
- Boot to ready: ~25s (NVMe)
- Inference: ~15 tokens/sec
- Model: Q4_K_M fits comfortably

**Recommended configuration:**
```yaml
inference:
  model:
    quantization: "Q4_K_M"
  server:
    max_model_len: 32768
voice:
  stt:
    model: "small"
```

---

#### Rockchip RK3588 Boards

Various boards based on RK3588 chip:

| Board | RAM | Price | Notes |
|-------|-----|-------|-------|
| Orange Pi 5 Plus | 16-32GB | $180 | Dual Ethernet |
| Rock 5B | 16GB | $160 | Good I/O |
| Radxa Rock 5A | 16GB | $140 | Compact |
| FriendlyElec NanoPC-T6 | 16GB | $200 | Enterprise |

**All RK3588 boards share:**
- 6 TOPS NPU (for future optimization)
- Mali-G610 GPU
- M.2 NVMe support
- Good Linux support

---

#### Mac Mini M4 (16GB+)

| Spec | Value |
|------|-------|
| SoC | Apple M4 |
| RAM | 16-32GB unified |
| GPU | 10-core integrated |
| Storage | 256GB+ SSD |
| Price | $600+ |

**Performance:**
- Boot to ready: ~15s
- Inference: ~30 tokens/sec
- Model: Q8 or even BF16 possible

**Notes:**
- Best performance per watt
- Requires macOS modifications for full OS replacement
- Can run AI-Native OS in VM/container

---

### Tier 2: Supported

These devices work but with limitations.

#### Raspberry Pi 5 (8GB)

| Spec | Value |
|------|-------|
| SoC | Broadcom BCM2712 |
| CPU | 4x Cortex-A76 @ 2.4GHz |
| RAM | 8GB LPDDR4X |
| GPU | VideoCore VII |
| Storage | microSD / NVMe (via HAT) |
| Price | ~$80 |

**Limitations:**
- 8GB RAM is tight for full stack
- Requires aggressive quantization (Q4_K_S)
- Reduced context length (16K recommended)
- Slower inference (~8 tokens/sec)

**Recommended configuration:**
```yaml
inference:
  model:
    quantization: "Q4_K_S"
  server:
    max_model_len: 16384
voice:
  stt:
    model: "tiny"  # Save RAM
memory:
  vectors:
    enabled: false  # Save RAM
```

**Essential:** Add NVMe HAT for acceptable boot times.

---

#### Khadas VIM4

| Spec | Value |
|------|-------|
| SoC | Amlogic A311D2 |
| CPU | 4x Cortex-A73 + 4x Cortex-A53 |
| RAM | 8GB |
| NPU | 3.2 TOPS |
| Price | ~$200 |

**Notes:**
- Good NPU for future optimization
- 8GB RAM is limiting factor

---

### Tier 3: Experimental

These devices may work but are not fully tested.

| Device | RAM | Notes |
|--------|-----|-------|
| NVIDIA Jetson Orin Nano | 8GB | Good GPU, limited RAM |
| Pine64 ROCKPro64 | 4GB | Insufficient RAM |
| Raspberry Pi 4 | 8GB | Too slow for practical use |
| BeagleBone AI-64 | 4GB | Insufficient RAM |

---

## Storage Recommendations

### Storage Types

| Type | Read Speed | Boot Time | Recommendation |
|------|------------|-----------|----------------|
| **NVMe SSD** | 3500 MB/s | ~25s | ✅ Strongly recommended |
| **SATA SSD** | 500 MB/s | ~35s | ✅ Good alternative |
| **eMMC** | 300 MB/s | ~45s | ⚠️ Acceptable |
| **microSD** | 100 MB/s | ~90s | ❌ Avoid for main storage |

### Recommended SSDs

| SSD | Capacity | Price | Notes |
|-----|----------|-------|-------|
| Samsung 980 | 256GB | $35 | Reliable |
| WD Black SN770 | 256GB | $30 | Good value |
| Crucial P3 | 500GB | $45 | Budget option |

### Partition Layout

```
Device: 256GB NVMe

Partition 1: /boot     256MB   FAT32
Partition 2: /         32GB    ext4
Partition 3: /var      64GB    ext4 (AI models, data)
Partition 4: /home     Rest    ext4 (user data)
```

---

## Memory Configurations

### 8GB RAM (Minimal)

```
┌────────────────────────────────────────┐
│ Linux kernel + base           ~300MB  │
│ vLLM runtime                  ~200MB  │
│ GLM-4.6V-Flash Q4_K_S         ~5GB   │
│ Whisper (tiny)                ~200MB  │
│ Pocket-TTS                    ~150MB  │
│ Memos                         ~50MB   │
│ ─────────────────────────────────────│
│ Total:                        ~5.9GB  │
│ Free:                         ~2.1GB  │
└────────────────────────────────────────┘

Trade-offs:
- No vector store (Qdrant)
- Reduced context (16K)
- Basic STT (tiny model)
- No browser agent
```

### 16GB RAM (Recommended)

```
┌────────────────────────────────────────┐
│ Linux kernel + base           ~300MB  │
│ vLLM runtime                  ~200MB  │
│ GLM-4.6V-Flash Q4_K_M         ~6GB   │
│ Whisper (small)               ~500MB  │
│ Pocket-TTS                    ~150MB  │
│ Memos                         ~50MB   │
│ Qdrant                        ~100MB  │
│ Clawdbot                      ~150MB  │
│ CAMEL                         ~150MB  │
│ ─────────────────────────────────────│
│ Total:                        ~7.6GB  │
│ Free:                         ~8.4GB  │
└────────────────────────────────────────┘

Full functionality with headroom.
```

### 32GB RAM (Optimal)

```
┌────────────────────────────────────────┐
│ Linux + all services          ~1GB   │
│ GLM-4.6V-Flash Q8             ~10GB  │
│ Whisper (medium)              ~1.5GB  │
│ VoxCPM (advanced TTS)         ~1GB   │
│ Full RAG stack                ~500MB  │
│ Browser (WebKitGTK)           ~500MB  │
│ ─────────────────────────────────────│
│ Total:                        ~14.5GB │
│ Free:                         ~17.5GB │
└────────────────────────────────────────┘

Room for multiple models, advanced features.
```

---

## Power Requirements

### Power Consumption

| Device | Idle | Load | Recommended PSU |
|--------|------|------|-----------------|
| Orange Pi 5 | 5W | 15W | 5V/4A (20W) |
| RPi 5 | 3W | 12W | 5V/5A (27W official) |
| RK3588 boards | 5W | 20W | 12V/3A (36W) |
| Mac Mini M4 | 5W | 30W | Included PSU |

### UPS Recommendations

For always-on operation:

| UPS | Capacity | Runtime (RPi 5) | Price |
|-----|----------|-----------------|-------|
| PiJuice HAT | 12Wh | ~1 hour | $50 |
| Geekworm X728 | 20Wh | ~2 hours | $40 |
| Generic USB-C | 50Wh | ~4 hours | $30 |

---

## Cooling

### Passive Cooling

Sufficient for:
- Raspberry Pi 5 (with official heatsink)
- Orange Pi 5 (with heatsink case)

### Active Cooling

Required for sustained inference:
- Any RK3588 board under heavy load
- Recommended: PWM-controlled fan

### Thermal Throttling Thresholds

| Device | Throttle | Shutdown |
|--------|----------|----------|
| RPi 5 | 80°C | 85°C |
| RK3588 | 85°C | 95°C |

---

## Peripheral Requirements

### Essential

| Peripheral | Purpose | Recommendation |
|------------|---------|----------------|
| **Microphone** | Voice input | USB conference mic |
| **Speaker** | Voice output | 3.5mm or USB speaker |
| **Network** | Connectivity | Ethernet preferred |

### Optional

| Peripheral | Purpose | Recommendation |
|------------|---------|----------------|
| Camera | Vision input | USB webcam (720p+) |
| Display | Debug/status | HDMI monitor or small LCD |
| Keyboard | Initial setup | USB keyboard |

### Recommended Microphones

| Microphone | Type | Price | Notes |
|------------|------|-------|-------|
| ReSpeaker USB | Array | $30 | Good noise cancellation |
| Anker PowerConf | Conference | $50 | Excellent quality |
| Generic USB | Single | $10 | Basic, works |

---

## Device-Specific Setup

### Orange Pi 5 Setup

```bash
# 1. Download Armbian image
wget https://armbian.com/orangepi5

# 2. Flash to NVMe (via USB adapter)
dd if=armbian.img of=/dev/sdX bs=4M

# 3. Boot and expand filesystem
sudo armbian-config

# 4. Install AI-Native OS
curl -sSL https://ainative.dev/install.sh | bash
```

### Raspberry Pi 5 Setup

```bash
# 1. Use Raspberry Pi Imager
# Select "Raspberry Pi OS Lite (64-bit)"

# 2. Add NVMe HAT and boot from NVMe
sudo raspi-config
# Advanced → Boot Order → NVMe

# 3. Install AI-Native OS
curl -sSL https://ainative.dev/install.sh | bash
```

---

## Performance Benchmarks

### Inference Speed (tokens/sec)

| Device | Q4_K_S | Q4_K_M | Q8 |
|--------|--------|--------|-----|
| Mac Mini M4 | 40 | 35 | 30 |
| Orange Pi 5 (16GB) | 18 | 15 | N/A |
| RPi 5 (8GB) | 10 | 8 | N/A |

### Boot Time (to ready)

| Device | SD Card | NVMe |
|--------|---------|------|
| Orange Pi 5 | 90s | 25s |
| RPi 5 | 120s | 40s |
| Mac Mini M4 | N/A | 15s |

### Voice Latency (end-to-end)

| Device | Simple query | With tools |
|--------|--------------|------------|
| Mac Mini M4 | 1.2s | 2.5s |
| Orange Pi 5 | 2.0s | 4.0s |
| RPi 5 | 3.5s | 7.0s |

---

## Buying Guide

### Budget Build (~$150)

```
Orange Pi 5 (8GB)      $90
256GB NVMe SSD         $35
Heatsink case          $15
USB microphone         $10
─────────────────────────
Total:                 $150
```

**Limitations:** 8GB RAM requires compromises.

### Recommended Build (~$250)

```
Orange Pi 5 (16GB)     $150
256GB NVMe SSD         $35
Active cooling case    $25
ReSpeaker USB mic      $30
USB speaker            $10
─────────────────────────
Total:                 $250
```

**Best value:** Full functionality at reasonable cost.

### Premium Build (~$700)

```
Mac Mini M4 (16GB)     $600
USB microphone         $50
USB speaker            $20
─────────────────────────
Total:                 $670
```

**Best performance:** Fastest inference, best experience.

---

## Related Documentation

- [Boot Sequence](boot-sequence.md) - Device-specific boot settings
- [Configuration](configuration.md) - Hardware-specific configuration
- [Architecture Stack](../architecture/stack.md) - Resource requirements
