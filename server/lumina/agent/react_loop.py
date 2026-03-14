import json
import logging
from typing import Callable, Awaitable, List, Dict, Any, Optional, Tuple
from .llm_client import LLMClient, ChatMessage, ToolDefinition, LLMResponse

logger = logging.getLogger(__name__)


class ReActLoop:
    """单次用户请求的 ReAct 推理循环。"""

    def __init__(
        self,
        llm_client: LLMClient,
        messages: List[ChatMessage],
        tools: Dict[str, Tuple[ToolDefinition, Callable[..., Awaitable[str]]]],
        max_iterations: int = 10,
        on_status: Optional[Callable[[str, str], Awaitable[None]]] = None,
    ) -> None:
        self.llm_client = llm_client
        self.messages = messages
        self.tools = tools
        self.max_iterations = max_iterations
        self.on_status = on_status

    async def run(self) -> str:
        """执行循环直到获得最终回复或达到最大迭代次数。"""
        iterations = 0
        
        while iterations < self.max_iterations:
            iterations += 1
            
            # 提取工具定义列表
            tool_definitions = [t[0] for t in self.tools.values()] if self.tools else None
            
            # 发送状态更新
            if self.on_status:
                await self.on_status("thinking", f"正在思考 (第 {iterations} 轮)...")
            
            try:
                response = await self.llm_client.chat(self.messages, tools=tool_definitions)
            except Exception as e:
                logger.exception("LLM call failed")
                return f"抱歉，我在思考时遇到了问题：{str(e)}"

            message = response.message
            self.messages.append(message)
            
            # 如果没有工具调用，说明是最终回复
            if not message.tool_calls:
                return message.content or "未收到模型回复。"

            # 处理工具调用
            if self.on_status:
                await self.on_status("acting", f"正在执行 {len(message.tool_calls)} 个操作...")

            for tool_call in message.tool_calls:
                tool_id = tool_call["id"]
                function_data = tool_call["function"]
                tool_name = function_data["name"]
                tool_args_raw = function_data["arguments"]
                
                logger.info(f"Tool call: {tool_name}({tool_args_raw})")
                
                if tool_name not in self.tools:
                    observation = f"错误：未找到工具 {tool_name}"
                else:
                    try:
                        args = json.loads(tool_args_raw)
                        handler = self.tools[tool_name][1]
                        observation = await handler(**args)
                    except Exception as e:
                        logger.exception(f"Tool {tool_name} execution failed")
                        observation = f"错误：执行工具 {tool_name} 时发生异常：{str(e)}"
                
                # 将观察结果添加到消息历史
                self.messages.append(ChatMessage(
                    role="tool",
                    content=observation,
                    tool_call_id=tool_id,
                    name=tool_name
                ))
        
        return "抱歉，我思考了太久，暂时无法给出最终结论。"
