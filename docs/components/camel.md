# CAMEL

CAMEL (Communicative Agents for "Mind" Exploration of Large Language Models) serves as the multi-agent orchestration layer for AI-Native OS.

## Overview

| Attribute | Value |
|-----------|-------|
| Repository | [camel-ai/camel](https://github.com/camel-ai/camel) |
| Language | Python |
| License | Apache 2.0 |
| Stars | 15,600+ |
| Role | Orchestration Layer |

## Why CAMEL?

| Feature | CAMEL | LangChain | AutoGen | CrewAI |
|---------|-------|-----------|---------|--------|
| Multi-agent native | ✅ | ⚠️ | ✅ | ✅ |
| Local model support | ✅ | ✅ | ✅ | ✅ |
| Memory/RAG | ✅ | ✅ | ⚠️ | ⚠️ |
| Societies/Roles | ✅ | ❌ | ✅ | ✅ |
| Scale (1M agents) | ✅ | ❌ | ❌ | ❌ |
| MCP Protocol | ✅ | ⚠️ | ❌ | ❌ |
| Footprint | ~50MB | ~100MB | ~80MB | ~40MB |

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                           CAMEL                                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                        Agents                                │  │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────┐  │  │
│  │  │  System   │ │ Assistant │ │  Browser  │ │   Vision    │  │  │
│  │  │   Agent   │ │   Agent   │ │   Agent   │ │   Agent     │  │  │
│  │  └───────────┘ └───────────┘ └───────────┘ └─────────────┘  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                      Societies                               │  │
│  │           Role-Playing • Workforce • Coordination            │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐  │
│  │   Memory    │ │  Toolkits   │ │        Models               │  │
│  │ (Memos/RAG) │ │ (MCP Tools) │ │ (vLLM/Ollama/OpenAI)        │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
camel/
├── agents/          # Agent implementations
│   ├── chat_agent.py
│   ├── task_agent.py
│   └── critic_agent.py
├── societies/       # Multi-agent coordination
│   ├── role_playing.py
│   └── workforce.py
├── models/          # LLM backends
│   ├── openai_model.py
│   ├── ollama_model.py
│   └── vllm_model.py
├── memories/        # Memory systems
│   ├── chat_history.py
│   ├── vector_memory.py
│   └── long_term_memory.py
├── toolkits/        # Available tools
│   ├── terminal.py
│   ├── file_toolkit.py
│   ├── browser_toolkit.py
│   └── code_execution.py
├── retrievers/      # RAG components
├── embeddings/      # Vector generation
└── interpreters/    # Code execution
```

## Installation

```bash
# Core only (~50MB)
pip install camel-ai

# With tools (~70MB)
pip install 'camel-ai[tools]'

# With RAG (~150MB)
pip install 'camel-ai[rag]'

# Everything (~300MB)
pip install 'camel-ai[all]'
```

## Local Model Configuration

### Using vLLM (Recommended)

```python
from camel.models import ModelFactory
from camel.types import ModelPlatformType

model = ModelFactory.create(
    model_platform=ModelPlatformType.VLLM,
    model_type="glm-4.6v-flash",
    url="http://localhost:8000/v1",
)
```

### Using Ollama

```python
model = ModelFactory.create(
    model_platform=ModelPlatformType.OLLAMA,
    model_type="glm-4.6v-flash",
    url="http://localhost:11434/v1",
)
```

> **Note**: vLLM is recommended over Ollama for better tool calling support.

## Agent Configuration

### System Agent

Controls OS-level operations.

```python
from camel.agents import ChatAgent
from camel.toolkits import TerminalToolkit, FileToolkit

system_agent = ChatAgent(
    system_message="""You are the System Agent for AI-Native OS.
    You can manage services, processes, and system configuration.
    Always confirm destructive actions with the user.""",
    model=model,
    tools=[
        *TerminalToolkit().get_tools(),
        *FileToolkit().get_tools(),
    ]
)
```

### Assistant Agent

Handles user-facing tasks.

```python
assistant_agent = ChatAgent(
    system_message="""You are a helpful personal assistant.
    You help with tasks, answer questions, and manage the user's schedule.""",
    model=model,
    tools=[
        *CalendarToolkit().get_tools(),
        *NotesToolkit().get_tools(),
    ]
)
```

### Browser Agent

Automates web interactions.

```python
from camel.toolkits import BrowserToolkit

browser_agent = ChatAgent(
    system_message="""You are a Browser Agent.
    You navigate websites, fill forms, and extract information.""",
    model=model,
    tools=BrowserToolkit().get_tools()
)
```

### Vision Agent

Processes visual input.

```python
vision_agent = ChatAgent(
    system_message="""You are a Vision Agent.
    You analyze screenshots, camera input, and documents.""",
    model=model,  # GLM-4.6V-Flash has native vision
)
```

## Multi-Agent Societies

### Role-Playing

Two agents collaborate on a task.

```python
from camel.societies import RolePlaying

session = RolePlaying(
    assistant_role="DevOps Engineer",
    user_role="System Architect",
    task="Design the boot sequence for AI-Native OS",
    model=model,
)

# Run the conversation
while not session.is_complete():
    response = await session.step()
    print(response)
```

### Workforce

Team of specialized agents.

```python
from camel.societies import Workforce

team = Workforce(
    agents=[
        ChatAgent(role="Backend Developer", model=model),
        ChatAgent(role="Frontend Developer", model=model),
        ChatAgent(role="Security Auditor", model=model),
    ]
)

result = await team.process("Build a user authentication system")
```

## Memory Integration

### With Memos Backend

```python
from camel.memories import LongTermMemory

memory = LongTermMemory(
    storage_path="/var/aios/memory",
    # Connect to Memos API
    backend_url="http://localhost:5230"
)

agent = ChatAgent(
    model=model,
    memory=memory,
)
```

### With Vector Store (RAG)

```python
from camel.memories import VectorDBMemory
from camel.storages import QdrantStorage

memory = VectorDBMemory(
    storage=QdrantStorage(path="/var/aios/vectors"),
    embedding_model=embedding_model,
)
```

## Tool System

### Built-in Toolkits

| Toolkit | Functions |
|---------|-----------|
| TerminalToolkit | bash, systemctl, ps, kill |
| FileToolkit | read, write, search, delete |
| BrowserToolkit | navigate, click, type, screenshot |
| CodeExecutionToolkit | run Python/JS code |
| SearchToolkit | web search |

### Custom Tools

```python
from camel.toolkits import BaseToolkit
from camel.functions import OpenAIFunction

class AIOSToolkit(BaseToolkit):
    @OpenAIFunction
    def get_system_status(self) -> str:
        """Get current CPU, RAM, and disk usage."""
        import psutil
        return f"CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%"

    @OpenAIFunction
    def take_screenshot(self) -> bytes:
        """Capture the current screen."""
        import pyautogui
        return pyautogui.screenshot()

    @OpenAIFunction
    def manage_service(self, name: str, action: str) -> str:
        """Start, stop, or restart a system service.

        Args:
            name: Service name
            action: One of 'start', 'stop', 'restart'
        """
        import subprocess
        result = subprocess.run(
            ['systemctl', action, name],
            capture_output=True, text=True
        )
        return result.stdout or result.stderr
```

## MCP Protocol Support

CAMEL supports the Model Context Protocol for standardized tool interaction.

```python
from camel.toolkits import MCPToolkit

# Load MCP-compatible tools
mcp_tools = MCPToolkit(
    config_path="/etc/aios/mcp-tools.json"
)

agent = ChatAgent(
    model=model,
    tools=mcp_tools.get_tools()
)
```

## AI-Native OS Integration

### Main Orchestrator

```python
# /etc/aios/orchestrator.py
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.types import ModelPlatformType

class AIOSOrchestrator:
    def __init__(self):
        self.model = ModelFactory.create(
            model_platform=ModelPlatformType.VLLM,
            model_type="glm-4.6v-flash",
            url="http://localhost:8000/v1",
        )

        self.agents = {
            'system': self._create_system_agent(),
            'assistant': self._create_assistant_agent(),
            'browser': self._create_browser_agent(),
            'vision': self._create_vision_agent(),
        }

    async def process(self, request):
        # 1. Determine which agent(s) to use
        agent = self._route_request(request)

        # 2. Enrich with memory context
        context = await self._get_context(request)

        # 3. Process with agent
        response = await agent.run(
            user_message=request.text,
            context=context,
            image=request.image  # if present
        )

        # 4. Save to memory
        await self._save_interaction(request, response)

        return response
```

## Resource Usage

| Metric | Value |
|--------|-------|
| RAM (core) | ~50MB |
| RAM (with tools) | ~100MB |
| RAM (full) | ~150MB |
| Storage | ~50MB |

## Related Documentation

- [GLM-4.6V-Flash](glm-model.md) - The model powering CAMEL agents
- [Memos](memos.md) - Memory backend integration
- [Configuration](../guides/configuration.md) - Agent configuration reference
