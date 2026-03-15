import asyncio
import logging
from typing import List, Optional
from .base import BaseTool, RiskLevel
from ..ws.protocol import Message, MessageType
from ..ws.server import LuminaWSServer

logger = logging.getLogger(__name__)


class AskUserTool(BaseTool):
    name = "ask_user"
    description = (
        "向用户提出问题并等待回复。"
        "当你不确定用户的意图、缺少关键信息、或需要用户在多个方案间做选择时使用此工具。"
        "支持自由文本回复和选择题两种模式。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "要向用户提出的问题"
            },
            "choices": {
                "type": "array",
                "items": {"type": "string"},
                "description": "可选。提供选项列表则为选择题模式，用户从中选择。不提供则为自由文本输入。"
            }
        },
        "required": ["question"]
    }
    risk_level = RiskLevel.LOW

    def __init__(self, ws_server: LuminaWSServer) -> None:
        self.ws_server = ws_server

    async def execute(self, question: str, choices: Optional[List[str]] = None) -> str:
        try:
            payload = {"question": question}
            if choices:
                payload["choices"] = choices
            
            prompt_msg = Message(
                type=MessageType.USER_PROMPT,
                payload=payload
            )
            
            logger.info(f"Asking user: {question}")
            response_msg = await self.ws_server.request(prompt_msg)
            
            answer = response_msg.payload.get("answer")
            if answer is not None:
                return str(answer)
            else:
                return "用户未提供有效回答。"
        except asyncio.TimeoutError:
            return "错误：等待用户回复超时。"
        except Exception as e:
            logger.exception("Error in AskUserTool")
            return f"错误：与用户交互时发生异常：{str(e)}"


class NotifyUserTool(BaseTool):
    name = "notify_user"
    description = (
        "向用户展示一条通知消息。不等待用户回复，立即返回。"
        "适用于告知用户任务进度、操作结果或提醒信息。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "要展示给用户的消息内容"
            }
        },
        "required": ["message"]
    }
    risk_level = RiskLevel.LOW

    def __init__(self, ws_server: LuminaWSServer) -> None:
        self.ws_server = ws_server

    async def execute(self, message: str) -> str:
        try:
            notify_msg = Message(
                type=MessageType.PET_COMMAND,
                payload={
                    "command": "show_bubble",
                    "data": {"text": message, "timeout": 5.0}
                }
            )
            await self.ws_server.send(notify_msg)
            return f"已向用户发送通知：{message}"
        except Exception as e:
            logger.exception("Error in NotifyUserTool")
            return f"错误：发送通知失败：{str(e)}"
