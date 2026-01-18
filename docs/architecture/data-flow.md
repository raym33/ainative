# Data Flow

This document describes how data moves through the AI-Native OS from user input to response output.

## Request Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  1. INPUT                                                                │
│     │                                                                    │
│     ├── Voice ──→ Whisper.cpp ──→ Text                                  │
│     ├── WhatsApp/Telegram/etc ──→ Clawdbot ──→ Text                     │
│     └── Screenshot/Camera ──→ Image bytes                                │
│                                      │                                   │
│                                      ▼                                   │
│  2. ROUTING                                                              │
│     │                                                                    │
│     └── CAMEL receives (text + optional image)                          │
│         ├── Check memory (Memos) for context                            │
│         ├── Select appropriate agent(s)                                  │
│         └── Build prompt with tools                                      │
│                                      │                                   │
│                                      ▼                                   │
│  3. INFERENCE                                                            │
│     │                                                                    │
│     └── GLM-4.6V-Flash (via vLLM)                                       │
│         ├── Analyze input (text + vision if present)                    │
│         ├── Decide: respond directly OR call tools                      │
│         └── Generate response / tool calls                              │
│                                      │                                   │
│                                      ▼                                   │
│  4. EXECUTION (if tools called)                                          │
│     │                                                                    │
│     └── MCP Tools execute in sandbox                                    │
│         ├── Terminal commands                                            │
│         ├── File operations                                              │
│         ├── Browser actions                                              │
│         └── Return results to model                                      │
│                                      │                                   │
│                                      ▼                                   │
│  5. OUTPUT                                                               │
│     │                                                                    │
│     ├── Text ──→ Pocket-TTS ──→ Voice                                   │
│     ├── Text ──→ Clawdbot ──→ WhatsApp/Telegram/etc                     │
│     └── Update memory (Memos) with interaction                          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Detailed Flow

### Stage 1: Input Collection

All user inputs are normalized into a common format before processing.

**Voice Input:**
```
Microphone → Whisper.cpp → {
  "type": "voice",
  "text": "What's the weather like?",
  "confidence": 0.95,
  "language": "en"
}
```

**Messaging Input:**
```
WhatsApp → Clawdbot Gateway → {
  "type": "message",
  "channel": "whatsapp",
  "user_id": "user123",
  "text": "Send me the report",
  "attachments": []
}
```

**Visual Input:**
```
Screenshot/Camera → {
  "type": "image",
  "format": "png",
  "data": <base64>,
  "source": "screen" | "camera"
}
```

### Stage 2: Context Enrichment

Before sending to the model, CAMEL enriches the request with context.

```python
# Pseudocode for context enrichment
async def enrich_context(request):
    # 1. Get user preferences
    user_prefs = await memos.get_user_preferences(request.user_id)

    # 2. Get relevant conversation history
    history = await memos.get_recent_conversations(
        user_id=request.user_id,
        limit=10
    )

    # 3. Search for relevant knowledge (RAG)
    if request.text:
        relevant_docs = await qdrant.search(
            query=request.text,
            top_k=5
        )

    # 4. Select appropriate agent
    agent = select_agent(request)

    # 5. Build enriched prompt
    return EnrichedRequest(
        original=request,
        user_prefs=user_prefs,
        history=history,
        knowledge=relevant_docs,
        agent=agent
    )
```

### Stage 3: Model Inference

The enriched request is sent to GLM-4.6V-Flash via vLLM.

```python
# Request to vLLM
{
    "model": "glm-4.6v-flash",
    "messages": [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": enriched_prompt},
            {"type": "image", "data": image_base64}  # if present
        ]}
    ],
    "tools": agent.available_tools,
    "max_tokens": 4096
}
```

**Response possibilities:**

1. **Direct response** (no tools needed):
```json
{
    "role": "assistant",
    "content": "The weather in Madrid is 22°C and sunny."
}
```

2. **Tool call** (action required):
```json
{
    "role": "assistant",
    "tool_calls": [{
        "id": "call_123",
        "function": {
            "name": "terminal_execute",
            "arguments": "{\"command\": \"curl wttr.in/Madrid\"}"
        }
    }]
}
```

### Stage 4: Tool Execution

If the model requests tool calls, they're executed in a sandboxed environment.

```python
async def execute_tools(tool_calls):
    results = []

    for call in tool_calls:
        # Execute in Podman container
        result = await sandbox.execute(
            tool=call.function.name,
            args=json.loads(call.function.arguments),
            timeout=30,
            permissions=get_permissions(call.function.name)
        )
        results.append({
            "tool_call_id": call.id,
            "output": result
        })

    # Send results back to model for final response
    return await model.continue_with_tool_results(results)
```

### Stage 5: Output Delivery

The final response is delivered through the appropriate channel.

```python
async def deliver_response(response, request):
    # 1. Save to memory
    await memos.save_interaction(
        user_id=request.user_id,
        input=request.text,
        output=response.content
    )

    # 2. Deliver via original channel
    if request.channel == "voice":
        audio = await pocket_tts.synthesize(response.content)
        await audio_output.play(audio)

    elif request.channel in ["whatsapp", "telegram", "discord"]:
        await clawdbot.send(
            channel=request.channel,
            user_id=request.user_id,
            message=response.content
        )
```

## Multi-Turn Conversations

For conversations that span multiple turns, context is maintained through:

1. **Short-term**: CAMEL's in-memory conversation buffer
2. **Medium-term**: Memos conversation history
3. **Long-term**: Qdrant vector embeddings for semantic search

```
Turn 1: "Find all PDF files on my desktop"
         → Tool call: file_search(path="~/Desktop", pattern="*.pdf")
         → "I found 5 PDF files: report.pdf, invoice.pdf..."

Turn 2: "Delete the oldest one"
         → Context: knows we're talking about PDF files
         → Tool call: file_delete(path="~/Desktop/old_report.pdf")
         → "I've deleted old_report.pdf"

Turn 3: "What did I ask you earlier?"
         → RAG search finds previous conversation
         → "You asked me to find PDF files and delete the oldest one"
```

## Error Handling

```
┌─────────────────────────────────────────────────────────┐
│                    Error Flow                           │
│                                                         │
│  Tool Failure ──→ Retry with backoff                   │
│       │                                                 │
│       └── Max retries ──→ Report to user               │
│                                                         │
│  Model Error ──→ Fallback response                     │
│                  "I'm having trouble processing that"   │
│                                                         │
│  Security Violation ──→ Block + Log + Alert            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Latency Breakdown

Typical end-to-end latency for a simple query:

| Stage | Time |
|-------|------|
| STT (Whisper) | ~200ms |
| Context enrichment | ~50ms |
| Model inference | ~500-2000ms |
| Tool execution | 0-5000ms (varies) |
| TTS (Pocket-TTS) | ~200ms |
| **Total (no tools)** | **~1s** |
| **Total (with tools)** | **~2-7s** |
