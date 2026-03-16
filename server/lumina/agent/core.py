from typing import Callable, Awaitable, List, Dict, Tuple, Optional
from .llm_client import LLMClient, ChatMessage, ToolDefinition
from .react_loop import ReActLoop


class AgentCore:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str,
        max_iterations: int = 10,
        history_window: int = 20,
    ) -> None:
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.history_window = history_window
        self.history: List[ChatMessage] = [
            ChatMessage(role="system", content=system_prompt)
        ]
        self.tools: Dict[str, Tuple[ToolDefinition, Callable[..., Awaitable[str]]]] = {}
        self._on_status: Optional[Callable[[str, str], Awaitable[None]]] = None

    def set_status_callback(self, callback: Callable[[str, str], Awaitable[None]]) -> None:
        """设置状态更新的回调函数。"""
        self._on_status = callback

    async def process_message(self, user_text: str) -> str:
        """处理用户消息，执行 ReAct 循环，返回最终回复文本。"""
        self.history.append(ChatMessage(role="user", content=user_text))
        
        # 执行 ReAct 推理循环
        loop = ReActLoop(
            llm_client=self.llm_client,
            messages=self.history,
            tools=self.tools,
            max_iterations=self.max_iterations,
            on_status=self._on_status,
        )
        
        reply = await loop.run()
        
        # 裁剪历史记录
        self._trim_history()
        
        return reply

    def register_tool(self, tool: ToolDefinition, handler: Callable[..., Awaitable[str]]) -> None:
        """注册一个可被 Agent 调用的工具。"""
        self.tools[tool.name] = (tool, handler)

    def get_conversation_history(self) -> List[ChatMessage]:
        """获取当前对话历史。"""
        return self.history

    def clear_history(self) -> None:
        """清空对话历史（保留系统提示词）。"""
        self.history = [ChatMessage(role="system", content=self.system_prompt)]

    def set_system_prompt(self, prompt: str) -> None:
        """更新系统提示词 / 角色人设。"""
        self.system_prompt = prompt
        if self.history and self.history[0].role == "system":
            self.history[0].content = prompt
        else:
            self.history.insert(0, ChatMessage(role="system", content=prompt))

    def _trim_history(self) -> None:
        """裁剪对话历史，保留系统提示词和最近的 window 轮对话。"""
        # 计算除了系统提示词以外的消息对
        # 一轮对话通常包括 user, tool_calls, tool_results, assistant
        # 这里简化处理：保留最近的 N 条消息
        if len(self.history) > self.history_window + 1:
            system_msg = self.history[0]
            self.history = [system_msg] + self.history[-(self.history_window):]
