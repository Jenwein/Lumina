import httpx
from dataclasses import dataclass
from typing import AsyncIterator, List, Dict, Optional, Any


@dataclass
class ChatMessage:
    role: str              # "system" | "user" | "assistant" | "tool"
    content: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"role": self.role, "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        if self.name:
            d["name"] = self.name
        return d


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]       # JSON Schema

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


@dataclass
class LLMResponse:
    message: ChatMessage
    usage: Optional[Dict[str, int]] = None  # {"prompt_tokens": ..., "completion_tokens": ...}
    finish_reason: str = "stop"


class LLMClient:
    def __init__(
        self,
        api_base: str,
        api_key: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> None:
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[ToolDefinition]] = None,
    ) -> LLMResponse:
        """发送聊天请求，返回模型响应。支持 Function Calling。"""
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        
        if tools:
            payload["tools"] = [t.to_dict() for t in tools]
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]
            msg_data = choice["message"]
            
            message = ChatMessage(
                role=msg_data["role"],
                content=msg_data.get("content"),
                tool_calls=msg_data.get("tool_calls"),
            )
            
            return LLMResponse(
                message=message,
                usage=data.get("usage"),
                finish_reason=choice.get("finish_reason", "stop"),
            )
