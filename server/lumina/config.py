import os
import yaml
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LuminaConfig:
    ws_host: str = "localhost"
    ws_port: int = 8765
    heartbeat_interval: float = 30.0
    heartbeat_timeout: float = 90.0

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
        
        # Environment variables override
        config.ws_host = os.getenv("LUMINA_WS_HOST", config.ws_host)
        config.ws_port = int(os.getenv("LUMINA_WS_PORT", str(config.ws_port)))
        
        return config
