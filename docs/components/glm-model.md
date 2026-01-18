# GLM-4.6V-Flash

GLM-4.6V-Flash is the core AI model for AI-Native OS, providing vision, tool use, and reasoning capabilities in a single 9B parameter model.

## Overview

| Attribute | Value |
|-----------|-------|
| Model | [zai-org/GLM-4.6V-Flash](https://huggingface.co/zai-org/GLM-4.6V-Flash) |
| Parameters | 9B (10B actual) |
| Context Window | 128K tokens |
| License | MIT |
| Role | Inference Layer - Core Model |

## Why GLM-4.6V-Flash?

This is the only ~9B parameter model that combines all three essential capabilities:

| Capability | Status | Description |
|------------|--------|-------------|
| **Vision** | ✅ Native | Process images, screenshots, documents |
| **Tool Use** | ✅ Native | Function calling without prompt hacking |
| **Reasoning** | ✅ Partial | `<think>` tags for chain-of-thought |

### Comparison with Alternatives

| Model | Params | Vision | Tools | Thinking | Context |
|-------|--------|--------|-------|----------|---------|
| **GLM-4.6V-Flash** | 9B | ✅ | ✅ | ✅ | 128K |
| Qwen2-VL | 7B | ✅ | ✅ | ❌ | 32K |
| Phi-3.5-Vision | 4B | ✅ | ⚠️ | ❌ | 128K |
| Llama 3.2 Vision | 11B | ✅ | ❌ | ❌ | 128K |
| DeepSeek-R1 | 7B | ❌ | ✅ | ✅ | 32K |

## Capabilities

### Vision

GLM-4.6V-Flash can process:
- Screenshots (for UI understanding)
- Camera input (for real-world interaction)
- Documents (PDFs, images of text)
- Charts and diagrams
- Handwritten notes (OCR)

```python
# Example: Analyze screenshot
response = model.generate(
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "data": screenshot_base64},
            {"type": "text", "text": "What applications are open?"}
        ]
    }]
)
```

### Tool Use (Function Calling)

Native support for function calling without special prompting.

```python
# Define tools
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

# Model will call tools when appropriate
response = model.generate(
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools
)

# Response includes tool calls
# {"tool_calls": [{"function": {"name": "get_weather", "arguments": "{\"location\": \"Tokyo\"}"}}]}
```

### Reasoning

Uses `<think>` tags for chain-of-thought reasoning.

```
User: How should I organize the boot sequence for the AI OS?

Model: <think>
Let me think through this step by step:
1. First, the kernel needs to initialize
2. Then mount filesystems
3. Start networking
4. Load the AI model (this is slow, ~30s)
5. Start interface services
6. Announce ready state
</think>

Here's my recommended boot sequence:
1. Kernel init (0-1s)
2. Filesystem mount (1-2s)
3. Networking (2-3s)
...
```

## Quantization Options

| Quantization | VRAM | System RAM | Quality | Recommended For |
|--------------|------|------------|---------|-----------------|
| BF16 | ~20GB | ~24GB | Best | Cloud/datacenter |
| Q8 | ~10GB | ~14GB | Excellent | Desktop with GPU |
| **Q4_K_M** | ~6GB | ~8GB | Good | **RPi 5 / Edge** |
| Q4_K_S | ~5GB | ~7GB | Acceptable | Minimal systems |

For AI-Native OS on ARM, **Q4_K_M** is recommended.

## Deployment

### With vLLM (Recommended)

```bash
# Install vLLM
pip install vllm

# Start server
python -m vllm.entrypoints.openai.api_server \
    --model zai-org/GLM-4.6V-Flash \
    --quantization awq \
    --max-model-len 32768 \
    --port 8000
```

### With Ollama

```bash
# Pull model (if available)
ollama pull glm-4.6v-flash

# Or create from GGUF
ollama create glm-4.6v-flash -f Modelfile

# Run
ollama serve
```

### With SGLang

```bash
pip install sglang

python -m sglang.launch_server \
    --model-path zai-org/GLM-4.6V-Flash \
    --port 8000
```

## API Usage

### OpenAI-Compatible Endpoint

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

# Text only
response = client.chat.completions.create(
    model="glm-4.6v-flash",
    messages=[{"role": "user", "content": "Hello!"}]
)

# With image
response = client.chat.completions.create(
    model="glm-4.6v-flash",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            {"type": "text", "text": "Describe this image"}
        ]
    }]
)

# With tools
response = client.chat.completions.create(
    model="glm-4.6v-flash",
    messages=[{"role": "user", "content": "What time is it in London?"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get current time in a timezone",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string"}
                }
            }
        }
    }]
)
```

## Performance on ARM

Tested on Orange Pi 5 (16GB RAM, RK3588):

| Metric | Q4_K_M |
|--------|--------|
| Load time | ~45s |
| First token | ~500ms |
| Tokens/sec | ~15 |
| VRAM usage | ~5.5GB |

Tested on Raspberry Pi 5 (8GB RAM):

| Metric | Q4_K_S |
|--------|--------|
| Load time | ~60s |
| First token | ~800ms |
| Tokens/sec | ~8 |
| RAM usage | ~6GB |

## Recommended Parameters

```python
# For general use
{
    "temperature": 0.8,
    "top_p": 0.6,
    "top_k": 2,
    "repetition_penalty": 1.1,
    "max_tokens": 4096
}

# For tool calling (more deterministic)
{
    "temperature": 0.3,
    "top_p": 0.9,
    "max_tokens": 2048
}

# For reasoning tasks
{
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 8192
}
```

## Limitations

1. **Text QA**: Pure text capabilities are slightly weaker than vision tasks
2. **Counting**: May struggle with precise counting in images
3. **Person identification**: Cannot reliably identify specific individuals
4. **Languages**: Primarily English and Chinese

## Model Family

GLM-4.6V-Flash is part of the GLM-V family:

| Model | Params | Target Use |
|-------|--------|------------|
| GLM-4.6V | 106B | Cloud, maximum capability |
| **GLM-4.6V-Flash** | 9B | Edge, local deployment |
| GLM-4.1V-Thinking | 9B | Enhanced reasoning |

## Related Documentation

- [CAMEL](camel.md) - Orchestration framework using this model
- [Stack](../architecture/stack.md) - Resource requirements
- [Hardware Guide](../guides/hardware.md) - Recommended devices
