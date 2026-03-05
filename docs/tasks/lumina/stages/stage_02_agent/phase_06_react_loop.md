# Phase 06: ReAct 自主循环

## §1 Goal
实现 Thought-Action-Observation 循环的 Agent 引擎，含工具注册表和异步调度。

## §2 Dependencies
- **Prerequisite phases**: Phase 05
- **Source files to read**: `server/src/lumina/llm/client.py`, `server/src/lumina/agent/`

## §3 Design & Constraints
- **Architecture principles**:
  - ReAct 模式：LLM 生成思考 + 选择工具 → 工具执行 → 结果回馈 → 循环直到完成
  - 工具注册表：工具声明 name、description、JSON Schema parameters
  - LLM function/tool calling 格式（OpenAI 兼容）
  - 每个会话维护独立的对话历史
  - 系统提示词可自定义（角色性格）
  - 最大迭代次数守卫，防止无限循环
  - Agent 发出事件流：thinking、tool_call、tool_result、response、error
- **Boundary conditions**:
  - 默认最大迭代次数 10，可配置
  - 工具执行超时默认 30 秒
  - 工具名称全局唯一，重复注册抛出异常
  - LLM 返回无效工具名时，Agent 将错误信息作为 observation 回馈 LLM
- **Out of scope**: 具体工具实现（仅注册表 + 调度框架）、UI 集成

## §4 Interface Contract

### 工具注册表

```python
# server/src/lumina/agent/tool_registry.py
from pydantic import BaseModel
from typing import Callable, Awaitable

class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict  # JSON Schema

class ToolResult(BaseModel):
    success: bool
    output: str
    error: str | None = None

class ToolRegistry:
    def register(self, spec: ToolSpec, handler: Callable[..., Awaitable[ToolResult]]) -> None: ...
    def unregister(self, name: str) -> None: ...
    def get_tools_schema(self) -> list[dict]: ...
    async def execute(self, name: str, arguments: dict) -> ToolResult: ...
    def list_tools(self) -> list[str]: ...
```

### Agent 引擎

```python
# server/src/lumina/agent/engine.py
from typing import AsyncIterator
from lumina.llm.client import LLMClient
from lumina.llm.models import Message

class AgentEvent(BaseModel):
    type: Literal["thinking", "tool_call", "tool_result", "response", "error"]
    content: str
    metadata: dict = {}

class AgentEngine:
    def __init__(
        self,
        llm: LLMClient,
        tools: ToolRegistry,
        system_prompt: str = "",
        max_iterations: int = 10,
    ): ...
    async def run(self, user_input: str) -> AsyncIterator[AgentEvent]: ...
    def set_system_prompt(self, prompt: str) -> None: ...
    def get_history(self) -> list[Message]: ...
    def clear_history(self) -> None: ...
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/agent/tool_registry.py` — ToolSpec、ToolResult、ToolRegistry 类
2. 创建 `server/src/lumina/agent/models.py` — AgentEvent 及辅助类型定义
3. 创建 `server/src/lumina/agent/engine.py` — AgentEngine，实现 ReAct 循环（思考→工具调用→观察→循环或完成）
4. 创建测试辅助工具 `server/tests/helpers/echo_tool.py` — 简单 echo 工具用于测试
5. 创建 `server/tests/test_agent.py` — 测试工具注册/注销、调度执行、ReAct 循环（mock LLM）
6. 测试最大迭代守卫和错误处理路径

## §6 Acceptance Criteria
- [ ] ToolRegistry 可注册/注销工具，返回 OpenAI function schema 格式
- [ ] ToolRegistry.execute 正确调用已注册工具并返回 ToolResult
- [ ] AgentEngine 运行 ReAct 循环：LLM 选择工具 → 工具执行 → 结果作为 observation → 循环或终结
- [ ] Agent 以 async iterator 形式发出事件流（thinking → tool_call → tool_result → response）
- [ ] 最大迭代守卫在达到上限时停止循环并发出 error 事件
- [ ] LLM 返回无效工具名时，Agent 优雅处理并将错误反馈给 LLM
- [ ] 所有测试通过：`uv run pytest server/tests/test_agent.py`

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
