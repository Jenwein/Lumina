import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    USER_MESSAGE = "user_message"
    USER_ACTION = "user_action"
    USER_PROMPT = "user_prompt"
    USER_PROMPT_RESPONSE = "user_prompt_response"
    CLIENT_READY = "client_ready"
    PET_COMMAND = "pet_command"
    AGENT_STATUS = "agent_status"
    CHAT_RESPONSE = "chat_response"
    CONFIRMATION_REQUEST = "confirmation_request"
    SERVER_READY = "server_ready"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class Message(BaseModel):
    type: MessageType
    payload: Dict[str, Any] = Field(default_factory=dict)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, raw: str) -> "Message":
        data = json.loads(raw)
        return cls(**data)
