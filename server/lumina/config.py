import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ModelConfig:
    name: str
    api_base: str
    api_key_env: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class AgentConfig:
    system_prompt: str = "你是 Lumina，一个活泼可爱的桌面助手。"
    max_react_iterations: int = 10
    history_window: int = 20


@dataclass
class LuminaConfig:
    ws_host: str = "localhost"
    ws_port: int = 8765
    heartbeat_interval: float = 30.0
    heartbeat_timeout: float = 90.0
    models: List[ModelConfig] = field(default_factory=list)
    active_model: str = "glm-4-flash"
    agent: AgentConfig = field(default_factory=AgentConfig)

    @classmethod
    def load(cls, path: str = "config.yaml") -> "LuminaConfig":
        config = cls()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    if "ws_host" in data:
                        config.ws_host = data["ws_host"]
                    if "ws_port" in data:
                        config.ws_port = data["ws_port"]
                    if "heartbeat_interval" in data:
                        config.heartbeat_interval = data["heartbeat_interval"]
                    if "heartbeat_timeout" in data:
                        config.heartbeat_timeout = data["heartbeat_timeout"]
                    
                    if "models" in data:
                        config.models = [ModelConfig(**m) for m in data["models"]]
                    if "active_model" in data:
                        config.active_model = data["active_model"]
                    if "agent" in data:
                        config.agent = AgentConfig(**data["agent"])
        
        # Environment variables override
        config.ws_host = os.getenv("LUMINA_WS_HOST", config.ws_host)
        config.ws_port = int(os.getenv("LUMINA_WS_PORT", str(config.ws_port)))
        
        return config
