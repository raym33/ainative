# Voice Stack

The voice stack provides speech-to-text (STT) and text-to-speech (TTS) capabilities for AI-Native OS, enabling voice-first interaction without cloud dependencies.

## Components

| Component | Role | Repository |
|-----------|------|------------|
| Whisper.cpp | Speech-to-Text | [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp) |
| Pocket-TTS | Text-to-Speech | [kyutai-labs/pocket-tts](https://github.com/kyutai-labs/pocket-tts) |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Voice Stack                               │
│                                                                 │
│   ┌─────────────────┐              ┌─────────────────┐         │
│   │   Microphone    │              │    Speaker      │         │
│   └────────┬────────┘              └────────▲────────┘         │
│            │                                │                   │
│            ▼                                │                   │
│   ┌─────────────────┐              ┌─────────────────┐         │
│   │  Whisper.cpp    │              │   Pocket-TTS    │         │
│   │                 │              │                 │         │
│   │  Audio → Text   │              │  Text → Audio   │         │
│   │                 │              │                 │         │
│   │  ~500MB RAM     │              │  ~150MB RAM     │         │
│   │  ~200ms latency │              │  ~200ms latency │         │
│   └────────┬────────┘              └────────▲────────┘         │
│            │                                │                   │
│            ▼                                │                   │
│   ┌─────────────────────────────────────────┴───────────────┐  │
│   │                    CAMEL Orchestrator                    │  │
│   │                                                          │  │
│   │  1. Receive transcribed text                            │  │
│   │  2. Process with GLM-4.6V-Flash                         │  │
│   │  3. Return response text                                │  │
│   │  4. Send to TTS                                         │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Whisper.cpp

### Overview

| Attribute | Value |
|-----------|-------|
| Repository | [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp) |
| Language | C++ |
| License | MIT |
| Stars | 35,000+ |

### Models

| Model | Size | RAM | Quality | Speed |
|-------|------|-----|---------|-------|
| tiny | 75MB | ~200MB | Basic | Fastest |
| base | 150MB | ~300MB | Fair | Fast |
| **small** | 500MB | ~500MB | Good | Balanced |
| medium | 1.5GB | ~1.5GB | Better | Slower |
| large | 3GB | ~3GB | Best | Slowest |

**Recommendation**: Use `small` model for AI-Native OS.

### Installation

```bash
# Clone repository
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp

# Build
make

# Download model
./models/download-ggml-model.sh small

# Test
./main -m models/ggml-small.bin -f samples/jfk.wav
```

### Running as Server

```bash
# Build server
make server

# Run on port 8081
./server -m models/ggml-small.bin --port 8081
```

### API Usage

```bash
# Transcribe audio file
curl http://localhost:8081/inference \
  -H "Content-Type: multipart/form-data" \
  -F file=@audio.wav

# Response
{
  "text": "Hello, how can I help you today?"
}
```

### Python Integration

```python
import requests

def transcribe(audio_path: str) -> str:
    with open(audio_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8081/inference',
            files={'file': f}
        )
    return response.json()['text']
```

### Performance on ARM

| Device | Model | First Token | Real-time Factor |
|--------|-------|-------------|------------------|
| RPi 5 | tiny | ~100ms | 0.3x |
| RPi 5 | small | ~200ms | 0.8x |
| Orange Pi 5 | small | ~150ms | 0.5x |
| Orange Pi 5 | medium | ~300ms | 1.2x |

---

## Pocket-TTS

### Overview

| Attribute | Value |
|-----------|-------|
| Repository | [kyutai-labs/pocket-tts](https://github.com/kyutai-labs/pocket-tts) |
| Language | Python (PyTorch) |
| License | Apache 2.0 |
| Model Size | 100M parameters |

### Key Features

- **CPU-only** - No GPU required
- **Low latency** - ~200ms to first audio chunk
- **Streaming** - Audio generated in real-time
- **Voice cloning** - Custom voices from samples
- **8 built-in voices** - Ready to use

### Built-in Voices

| Voice | Gender | Style |
|-------|--------|-------|
| Alba | Female | Neutral |
| Marius | Male | Neutral |
| Javert | Male | Authoritative |
| Jean | Male | Warm |
| Fantine | Female | Soft |
| Cosette | Female | Young |
| Eponine | Female | Expressive |
| Azelma | Female | Casual |

### Installation

```bash
# Install from PyPI
pip install pocket-tts

# Or from source
git clone https://github.com/kyutai-labs/pocket-tts
cd pocket-tts
pip install -e .
```

### Running as Server

```bash
# Start HTTP server on port 8080
pocket-tts-serve --port 8080
```

### API Usage

```bash
# Synthesize speech
curl -X POST http://localhost:8080/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am your AI assistant.", "voice": "alba"}' \
  --output response.wav
```

### Python Integration

```python
from pocket_tts import PocketTTS

tts = PocketTTS()

# Generate audio
audio = tts.synthesize(
    text="Hello, I am your AI assistant.",
    voice="alba"
)

# Save to file
audio.save("output.wav")

# Or stream
for chunk in tts.stream("This is a longer text..."):
    audio_output.play(chunk)
```

### Voice Cloning

```python
# Clone voice from audio sample
custom_voice = tts.clone_voice(
    audio_path="reference.wav",
    voice_name="my_voice"
)

# Use cloned voice
audio = tts.synthesize(
    text="Speaking with cloned voice.",
    voice="my_voice"
)
```

### Performance on ARM

| Device | Latency (first chunk) | Real-time Factor |
|--------|----------------------|------------------|
| RPi 5 | ~300ms | 4x |
| Orange Pi 5 | ~200ms | 6x |
| Mac Mini M4 | ~100ms | 10x |

---

## Integration with AI-Native OS

### Voice Input Handler

```python
# /etc/aios/voice_input.py
import asyncio
import sounddevice as sd
import numpy as np
import requests

class VoiceInput:
    def __init__(self, whisper_url="http://localhost:8081"):
        self.whisper_url = whisper_url
        self.sample_rate = 16000
        self.is_listening = False

    async def listen(self) -> str:
        """Record audio until silence, then transcribe."""
        self.is_listening = True
        audio_buffer = []

        def callback(indata, frames, time, status):
            if self.is_listening:
                audio_buffer.append(indata.copy())

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=callback
        ):
            # Wait for speech end (silence detection)
            await self._wait_for_silence(audio_buffer)

        self.is_listening = False

        # Combine and transcribe
        audio = np.concatenate(audio_buffer)
        return await self._transcribe(audio)

    async def _transcribe(self, audio: np.ndarray) -> str:
        # Save to temp file
        import tempfile
        import scipy.io.wavfile as wav

        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            wav.write(f.name, self.sample_rate, audio)
            with open(f.name, 'rb') as audio_file:
                response = requests.post(
                    f"{self.whisper_url}/inference",
                    files={'file': audio_file}
                )
        return response.json()['text']
```

### Voice Output Handler

```python
# /etc/aios/voice_output.py
import requests
import sounddevice as sd
import numpy as np

class VoiceOutput:
    def __init__(self, tts_url="http://localhost:8080"):
        self.tts_url = tts_url
        self.voice = "alba"
        self.sample_rate = 24000

    async def speak(self, text: str):
        """Convert text to speech and play."""
        response = requests.post(
            f"{self.tts_url}/synthesize",
            json={"text": text, "voice": self.voice}
        )

        # Play audio
        audio = np.frombuffer(response.content, dtype=np.int16)
        sd.play(audio, self.sample_rate)
        sd.wait()

    async def stream_speak(self, text: str):
        """Stream TTS for lower latency on long text."""
        response = requests.post(
            f"{self.tts_url}/stream",
            json={"text": text, "voice": self.voice},
            stream=True
        )

        for chunk in response.iter_content(chunk_size=4096):
            audio = np.frombuffer(chunk, dtype=np.int16)
            sd.play(audio, self.sample_rate)
```

### Complete Voice Loop

```python
# /etc/aios/voice_loop.py
from voice_input import VoiceInput
from voice_output import VoiceOutput
from orchestrator import AIOSOrchestrator

async def voice_loop():
    voice_in = VoiceInput()
    voice_out = VoiceOutput()
    orchestrator = AIOSOrchestrator()

    # Announce ready
    await voice_out.speak("AI OS ready. How can I help you?")

    while True:
        # Listen for input
        user_text = await voice_in.listen()

        if not user_text.strip():
            continue

        print(f"User: {user_text}")

        # Process with AI
        response = await orchestrator.process({
            "text": user_text,
            "channel": "voice"
        })

        print(f"AI: {response}")

        # Speak response
        await voice_out.speak(response)
```

---

## Resource Summary

| Component | RAM | Storage | CPU (active) |
|-----------|-----|---------|--------------|
| Whisper.cpp (small) | ~500MB | ~500MB | 50-100% |
| Pocket-TTS | ~150MB | ~100MB | 30-50% |
| **Total Voice Stack** | ~650MB | ~600MB | - |

---

## Alternative: VoxCPM (Advanced)

For systems with more resources, [VoxCPM](https://github.com/OpenBMB/VoxCPM) offers:
- Voice cloning with emotional adaptation
- Better prosody and naturalness
- Bilingual (English/Chinese)

**Trade-off**: Requires GPU, ~1GB+ VRAM

---

## Related Documentation

- [Clawdbot](clawdbot.md) - Integrating voice with messaging
- [CAMEL](camel.md) - Processing voice input
- [Boot Sequence](../guides/boot-sequence.md) - Voice service startup
