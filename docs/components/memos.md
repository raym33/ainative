# Memos

Memos serves as the knowledge base and persistent memory layer for AI-Native OS, providing long-term storage for user preferences, conversation history, and learned behaviors.

## Overview

| Attribute | Value |
|-----------|-------|
| Repository | [usememos/memos](https://github.com/usememos/memos) |
| Language | Go + React |
| License | MIT |
| Stars | 35,000+ |
| Role | Memory Layer - Knowledge Base |

## Why Memos?

| Feature | Benefit |
|---------|---------|
| Privacy-first | Zero telemetry, all data local |
| Self-hosted | No cloud dependency |
| Lightweight | Go binary + SQLite |
| REST + gRPC APIs | Easy integration |
| Markdown support | Rich content storage |
| Full export | Data portability |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Memos                                  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                     REST API                             │  │
│   │                  http://localhost:5230                   │  │
│   └─────────────────────────┬───────────────────────────────┘  │
│                             │                                   │
│   ┌─────────────────────────┼───────────────────────────────┐  │
│   │                    Core Service                          │  │
│   │                                                          │  │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │  │
│   │  │   Memos    │  │  Tags      │  │    Resources       │ │  │
│   │  │  (notes)   │  │  (labels)  │  │   (attachments)    │ │  │
│   │  └────────────┘  └────────────┘  └────────────────────┘ │  │
│   │                                                          │  │
│   └─────────────────────────┬───────────────────────────────┘  │
│                             │                                   │
│   ┌─────────────────────────┼───────────────────────────────┐  │
│   │                    Storage                               │  │
│   │                                                          │  │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │  │
│   │  │  SQLite    │  │   MySQL    │  │   PostgreSQL       │ │  │
│   │  │  (default) │  │ (optional) │  │   (optional)       │ │  │
│   │  └────────────┘  └────────────┘  └────────────────────┘ │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Docker (Recommended)

```bash
docker run -d \
  --name memos \
  -p 5230:5230 \
  -v /var/aios/memos:/var/opt/memos \
  ghcr.io/usememos/memos:latest
```

### Binary

```bash
# Download latest release
wget https://github.com/usememos/memos/releases/latest/download/memos-linux-arm64.tar.gz
tar -xzf memos-linux-arm64.tar.gz

# Run
./memos --mode prod --port 5230 --data /var/aios/memos
```

### From Source

```bash
git clone https://github.com/usememos/memos
cd memos

# Build backend
go build -o memos ./bin/memos/main.go

# Build frontend
cd web && pnpm install && pnpm build
```

## Data Model for AI-Native OS

### User Preferences

Store user settings and habits as tagged memos.

```markdown
#preferences #system

- Language: English
- Voice: alba
- Wake word: "Hey AI"
- Confirmation required: destructive actions
- Timezone: Europe/Madrid
```

### Conversation History

Store interactions for context.

```markdown
#conversation #2024-01-15

**User**: What's the weather like?
**AI**: It's 22°C and sunny in Madrid.

**User**: Remind me to water the plants tomorrow
**AI**: I've set a reminder for tomorrow at 9 AM.
```

### Learned Behaviors

Store patterns the AI has learned.

```markdown
#learned #patterns

- User prefers concise responses
- User often asks about weather in the morning
- User works from home on Mondays
- User's favorite music genre: jazz
```

### System Knowledge

Store system-specific information.

```markdown
#system #services

## Running Services
- vllm: http://localhost:8000
- whisper: http://localhost:8081
- pocket-tts: http://localhost:8080
- memos: http://localhost:5230

## Last Boot
- Time: 2024-01-15 08:30:00
- Duration: 45 seconds
- Status: All services healthy
```

## API Usage

### Authentication

```bash
# Create access token via UI, then use in requests
export MEMOS_TOKEN="your-access-token"
```

### Create Memo

```bash
curl -X POST http://localhost:5230/api/v1/memos \
  -H "Authorization: Bearer $MEMOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "#conversation User asked about the weather.",
    "visibility": "PRIVATE"
  }'
```

### Search Memos

```bash
# Search by tag
curl "http://localhost:5230/api/v1/memos?filter=tag:conversation" \
  -H "Authorization: Bearer $MEMOS_TOKEN"

# Search by content
curl "http://localhost:5230/api/v1/memos?filter=content:weather" \
  -H "Authorization: Bearer $MEMOS_TOKEN"
```

### List Memos

```bash
curl "http://localhost:5230/api/v1/memos?pageSize=10" \
  -H "Authorization: Bearer $MEMOS_TOKEN"
```

### Update Memo

```bash
curl -X PATCH http://localhost:5230/api/v1/memos/1 \
  -H "Authorization: Bearer $MEMOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated content here"
  }'
```

### Delete Memo

```bash
curl -X DELETE http://localhost:5230/api/v1/memos/1 \
  -H "Authorization: Bearer $MEMOS_TOKEN"
```

## Python Integration

```python
import requests

class MemosClient:
    def __init__(self, base_url="http://localhost:5230", token=None):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/json"
        }

    def create_memo(self, content: str, tags: list = None) -> dict:
        """Create a new memo."""
        # Add tags to content
        if tags:
            tag_str = " ".join(f"#{tag}" for tag in tags)
            content = f"{tag_str}\n\n{content}"

        response = requests.post(
            f"{self.base_url}/api/v1/memos",
            headers=self.headers,
            json={"content": content, "visibility": "PRIVATE"}
        )
        return response.json()

    def search(self, query: str = None, tag: str = None, limit: int = 10) -> list:
        """Search memos by content or tag."""
        params = {"pageSize": limit}

        if tag:
            params["filter"] = f"tag:{tag}"
        elif query:
            params["filter"] = f"content:{query}"

        response = requests.get(
            f"{self.base_url}/api/v1/memos",
            headers=self.headers,
            params=params
        )
        return response.json().get("memos", [])

    def get_user_preferences(self) -> dict:
        """Get user preferences from memos."""
        memos = self.search(tag="preferences")
        if not memos:
            return {}

        # Parse preferences from latest memo
        content = memos[0]["content"]
        prefs = {}
        for line in content.split("\n"):
            if ":" in line and line.startswith("- "):
                key, value = line[2:].split(":", 1)
                prefs[key.strip().lower()] = value.strip()
        return prefs

    def save_conversation(self, user_input: str, ai_response: str):
        """Save a conversation turn."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        content = f"""**User**: {user_input}
**AI**: {ai_response}"""

        self.create_memo(content, tags=["conversation", today])

    def get_recent_conversations(self, limit: int = 10) -> list:
        """Get recent conversation history."""
        return self.search(tag="conversation", limit=limit)
```

## Integration with CAMEL

```python
# /etc/aios/memory_backend.py
from camel.memories import BaseLongTermMemory
from memos_client import MemosClient

class MemosMemoryBackend(BaseLongTermMemory):
    def __init__(self, memos_url="http://localhost:5230", token=None):
        self.client = MemosClient(memos_url, token)

    def save(self, key: str, content: str, metadata: dict = None):
        """Save to long-term memory."""
        tags = ["memory", key]
        if metadata:
            tags.extend(metadata.get("tags", []))
        self.client.create_memo(content, tags=tags)

    def retrieve(self, query: str, top_k: int = 5) -> list:
        """Retrieve relevant memories."""
        return self.client.search(query=query, limit=top_k)

    def get_context(self, user_id: str) -> dict:
        """Get full context for a user."""
        return {
            "preferences": self.client.get_user_preferences(),
            "recent_conversations": self.client.get_recent_conversations(10),
            "learned_behaviors": self.client.search(tag="learned", limit=20)
        }
```

## Vector Search with Qdrant

For semantic search (RAG), combine Memos with Qdrant:

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class MemosRAG:
    def __init__(self, memos_client, qdrant_path="/var/aios/vectors"):
        self.memos = memos_client
        self.qdrant = QdrantClient(path=qdrant_path)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

        # Create collection if not exists
        self.qdrant.recreate_collection(
            collection_name="memos",
            vectors_config={"size": 384, "distance": "Cosine"}
        )

    def index_memo(self, memo: dict):
        """Index a memo for semantic search."""
        embedding = self.encoder.encode(memo["content"])
        self.qdrant.upsert(
            collection_name="memos",
            points=[{
                "id": memo["id"],
                "vector": embedding.tolist(),
                "payload": {"content": memo["content"]}
            }]
        )

    def semantic_search(self, query: str, top_k: int = 5) -> list:
        """Search memos by semantic similarity."""
        query_embedding = self.encoder.encode(query)
        results = self.qdrant.search(
            collection_name="memos",
            query_vector=query_embedding.tolist(),
            limit=top_k
        )
        return [hit.payload["content"] for hit in results]
```

## Resource Usage

| Metric | Value |
|--------|-------|
| RAM | ~50MB |
| Storage (base) | ~20MB |
| Storage (data) | Variable |
| CPU (idle) | <1% |

## Configuration

**Location**: `/etc/aios/memos.env`

```bash
# Server settings
MEMOS_MODE=prod
MEMOS_PORT=5230
MEMOS_DATA=/var/aios/memos

# Database (default: SQLite)
MEMOS_DRIVER=sqlite
MEMOS_DSN=/var/aios/memos/memos.db

# Optional: PostgreSQL
# MEMOS_DRIVER=postgres
# MEMOS_DSN=postgresql://user:pass@localhost:5432/memos
```

## Backup & Export

```bash
# Export all data
curl "http://localhost:5230/api/v1/export" \
  -H "Authorization: Bearer $MEMOS_TOKEN" \
  -o memos_backup.json

# Or simply copy SQLite file
cp /var/aios/memos/memos.db /backup/memos_$(date +%Y%m%d).db
```

## Related Documentation

- [CAMEL](camel.md) - Using Memos as memory backend
- [Architecture Overview](../architecture/overview.md) - Memory layer context
- [Configuration](../guides/configuration.md) - Full configuration reference
