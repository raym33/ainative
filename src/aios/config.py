"""
Configuration management for AI-Native OS.

Handles loading, validation, and access to system configuration.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import yaml


@dataclass
class InferenceConfig:
    """Configuration for the inference backend."""
    backend: str = "ollama"  # ollama or vllm
    model: str = "glm-4.6v-flash"
    url: str = "http://localhost:11434/v1"
    max_tokens: int = 4096
    temperature: float = 0.8
    top_p: float = 0.6


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""
    enabled: bool = True
    tools: list = field(default_factory=list)
    system_prompt: Optional[str] = None


@dataclass
class ToolsConfig:
    """Configuration for tool permissions."""
    terminal: Dict[str, Any] = field(default_factory=lambda: {
        "allowed_commands": ["ls", "cat", "grep", "find", "ps", "pwd", "echo", "date"],
        "blocked_commands": ["rm -rf", "dd", "mkfs", "fdisk"],
        "timeout": 30
    })
    files: Dict[str, Any] = field(default_factory=lambda: {
        "allowed_paths": [str(Path.home()), "/tmp"],
        "blocked_paths": ["/etc", "/boot", "/root", "/sys", "/proc"],
        "max_file_size": 10 * 1024 * 1024  # 10MB
    })


@dataclass
class VoiceConfig:
    """Configuration for voice services."""
    stt_enabled: bool = False
    stt_url: str = "http://localhost:8081"
    stt_model: str = "small"
    tts_enabled: bool = False
    tts_url: str = "http://localhost:8080"
    tts_voice: str = "alba"


@dataclass
class MemoryConfig:
    """Configuration for memory/storage."""
    backend: str = "simple"  # simple, memos, qdrant
    memos_url: str = "http://localhost:5230"
    max_history: int = 20


@dataclass
class Config:
    """Main configuration container for AI-Native OS."""

    # System settings
    name: str = "AIOS"
    version: str = "0.1.0"
    language: str = "en"
    log_level: str = "info"

    # Component configs
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load configuration from a YAML file.

        Args:
            path: Path to config file. If None, uses defaults.

        Returns:
            Config instance with loaded values.
        """
        config = cls()

        if path is None:
            # Try default locations
            default_paths = [
                Path.cwd() / "config.yaml",
                Path.cwd() / "aios.yaml",
                Path.home() / ".config" / "aios" / "config.yaml",
                Path("/etc/aios/config.yaml"),
            ]
            for p in default_paths:
                if p.exists():
                    path = str(p)
                    break

        if path and Path(path).exists():
            config._load_from_file(path)

        # Override with environment variables
        config._load_from_env()

        return config

    def _load_from_file(self, path: str) -> None:
        """Load values from a YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}

        # System settings
        self.name = data.get("system", {}).get("name", self.name)
        self.language = data.get("system", {}).get("language", self.language)
        self.log_level = data.get("system", {}).get("log_level", self.log_level)

        # Inference settings
        inf_data = data.get("inference", {})
        self.inference.backend = inf_data.get("backend", self.inference.backend)
        self.inference.model = inf_data.get("model", self.inference.model)
        self.inference.url = inf_data.get("url", self.inference.url)
        self.inference.max_tokens = inf_data.get("max_tokens", self.inference.max_tokens)
        self.inference.temperature = inf_data.get("temperature", self.inference.temperature)

        # Agent settings
        agents_data = data.get("agents", {})
        for agent_name, agent_conf in agents_data.items():
            self.agents[agent_name] = AgentConfig(
                enabled=agent_conf.get("enabled", True),
                tools=agent_conf.get("tools", []),
                system_prompt=agent_conf.get("system_prompt")
            )

        # Tools settings
        tools_data = data.get("tools", {})
        if "terminal" in tools_data:
            self.tools.terminal.update(tools_data["terminal"])
        if "files" in tools_data:
            self.tools.files.update(tools_data["files"])

        # Voice settings
        voice_data = data.get("voice", {})
        self.voice.stt_enabled = voice_data.get("stt", {}).get("enabled", self.voice.stt_enabled)
        self.voice.stt_url = voice_data.get("stt", {}).get("url", self.voice.stt_url)
        self.voice.tts_enabled = voice_data.get("tts", {}).get("enabled", self.voice.tts_enabled)
        self.voice.tts_url = voice_data.get("tts", {}).get("url", self.voice.tts_url)
        self.voice.tts_voice = voice_data.get("tts", {}).get("voice", self.voice.tts_voice)

        # Memory settings
        memory_data = data.get("memory", {})
        self.memory.backend = memory_data.get("backend", self.memory.backend)
        self.memory.max_history = memory_data.get("max_history", self.memory.max_history)

    def _load_from_env(self) -> None:
        """Override settings from environment variables."""
        # AIOS_INFERENCE_BACKEND, AIOS_INFERENCE_URL, etc.
        env_map = {
            "AIOS_INFERENCE_BACKEND": ("inference", "backend"),
            "AIOS_INFERENCE_MODEL": ("inference", "model"),
            "AIOS_INFERENCE_URL": ("inference", "url"),
            "AIOS_LOG_LEVEL": ("log_level", None),
            "AIOS_LANGUAGE": ("language", None),
        }

        for env_var, (attr, sub_attr) in env_map.items():
            value = os.environ.get(env_var)
            if value:
                if sub_attr:
                    obj = getattr(self, attr)
                    setattr(obj, sub_attr, value)
                else:
                    setattr(self, attr, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "system": {
                "name": self.name,
                "version": self.version,
                "language": self.language,
                "log_level": self.log_level,
            },
            "inference": {
                "backend": self.inference.backend,
                "model": self.inference.model,
                "url": self.inference.url,
                "max_tokens": self.inference.max_tokens,
                "temperature": self.inference.temperature,
            },
            "agents": {
                name: {"enabled": a.enabled, "tools": a.tools}
                for name, a in self.agents.items()
            },
            "tools": {
                "terminal": self.tools.terminal,
                "files": self.tools.files,
            },
            "voice": {
                "stt_enabled": self.voice.stt_enabled,
                "tts_enabled": self.voice.tts_enabled,
            },
            "memory": {
                "backend": self.memory.backend,
                "max_history": self.memory.max_history,
            },
        }


# Default configuration for quick access
DEFAULT_CONFIG = Config()
