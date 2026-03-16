from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict
from ..agent.llm_client import ToolDefinition


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]       # JSON Schema for arguments
    risk_level: RiskLevel = RiskLevel.LOW

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """执行工具操作，返回结果描述字符串。"""
        pass

    def to_tool_definition(self) -> ToolDefinition:
        """转换为 LLM ToolDefinition 格式。"""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )
