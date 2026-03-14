import json
import logging
from typing import Dict, List, Optional, Any
from .base import BaseTool, RiskLevel
from ..agent.llm_client import ToolDefinition

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self) -> None:
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册一个工具实例。"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[BaseTool]:
        """按名称获取工具。"""
        return self.tools.get(name)

    def list_definitions(self) -> List[ToolDefinition]:
        """获取所有已注册工具的 ToolDefinition 列表（传给 LLM）。"""
        return [tool.to_tool_definition() for tool in self.tools.values()]

    async def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """查找并执行指定工具，返回结果。"""
        tool = self.get(name)
        if not tool:
            return f"错误：未找到工具 {name}"

        # 检查风险等级
        if tool.risk_level == RiskLevel.HIGH:
            # Phase 07: 发送确认请求。本阶段仅打印警告并执行
            logger.warning(f"Executing HIGH RISK tool: {name} with args: {arguments}")
        elif tool.risk_level == RiskLevel.MEDIUM:
            logger.info(f"Executing MEDIUM RISK tool: {name} with args: {arguments}")

        try:
            # 捕获工具执行中的任何异常，返回友好的描述而不是堆栈跟踪
            result = await tool.execute(**arguments)
            return result
        except Exception as e:
            logger.exception(f"Tool execution failed: {name}")
            return f"错误：执行工具 {name} 时发生异常：{str(e)}"
