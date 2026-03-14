# Phase 03: Agent 决策引擎

## §1 Goal

实现基于 ReAct (Reasoning + Acting) 模式的 Agent 决策引擎，集成 OpenAI 兼容格式的多模型 LLM 客户端，支持角色人设、对话历史管理和自主任务循环。本阶段完成后，Agent 能通过对话理解用户意图并生成结构化的行动计划（但尚未接入实际工具执行）。

## §2 Dependencies

- **Prerequisite phases**: Phase 01 (`[x] Done`)
- **Reference Materials**:
    - [ ] [PRD — Agent 决策引擎](../../../PRD.md) §2.1
    - [ ] [OpenAI Chat Completions API 参考](https://platform.openai.com/docs/api-reference/chat)
    - [ ] [GLM-4 API 文档](https://open.bigmodel.cn/dev/api/normal-model/glm-4)
    - [ ] [GLM-4-Flash 测试 API Key](../../../GLM_APIKEY) — `glm-4-flash` 模型
- **Source files to read**:
    - [ ] `server/lumina/ws/server.py` (Phase 01 产出)
    - [ ] `server/lumina/ws/protocol.py` (Phase 01 产出)
    - [ ] `server/lumina/config.py` (Phase 01 产出)

## §3 Design & Constraints

### ReAct 循环架构

Agent 采用经典 ReAct 模式进行自主推理：

```
用户输入
   │
   ▼
┌──────────────────────────────────────┐
│           ReAct Loop                 │
│                                      │
│  ┌──────────┐                        │
│  │ Thought  │ LLM 分析当前状态       │
│  └────┬─────┘                        │
│       │                              │
│       ▼                              │
│  ┌──────────┐    无需行动            │
│  │ Decision │───────────► 最终回复    │
│  └────┬─────┘                        │
│       │ 需要行动                     │
│       ▼                              │
│  ┌──────────┐                        │
│  │  Action  │ 选择工具 + 参数        │
│  └────┬─────┘                        │
│       │                              │
│       ▼                              │
│  ┌──────────────┐                    │
│  │ Observation  │ 接收工具返回结果    │
│  └──────┬───────┘                    │
│         │                            │
│         └──────► 回到 Thought        │
└──────────────────────────────────────┘
```

**关键约束**:
- 单次循环最大迭代次数: 10 (可配置，防止无限循环)
- 每次 Thought 都会通过 WebSocket 发送 `agent_status` 更新前端状态
- Action 调用采用 OpenAI Function Calling 格式 (tool_calls)

### LLM 客户端设计

统一使用 OpenAI 兼容 API 格式，通过配置切换不同提供商：

```yaml
# config.yaml 示例
models:
  - name: "glm-4-flash"
    api_base: "https://open.bigmodel.cn/api/paas/v4/"
    api_key_env: "GLM_API_KEY"    # 从环境变量读取
    model: "glm-4-flash"
    max_tokens: 4096
    temperature: 0.7
  - name: "deepseek-chat"
    api_base: "https://api.deepseek.com/v1/"
    api_key_env: "DEEPSEEK_API_KEY"
    model: "deepseek-chat"
    max_tokens: 4096
active_model: "glm-4-flash"
```

### 角色与记忆系统

- **系统提示词**: 定义桌宠的性格、语气和行为准则，存储在配置文件中
- **对话历史**: 维护滑动窗口式的对话记录，防止 token 超限
  - 策略: 保留最近 N 轮对话 + 始终保留系统提示词
  - 默认 N = 20 轮 (可配置)
- **上下文注入**: 每次 LLM 调用前，自动注入当前系统状态摘要（时间、活动窗口等）

### 消息流转

```
Godot (user_message) ──► WebSocket Server ──► Agent.process_message()
                                                     │
                                                     ▼
                                              LLM Client.chat()
                                                     │
                                                     ▼
                                              ReAct 循环 (可能多轮)
                                                     │
                                              ┌──────┴──────┐
                                              │             │
                                        agent_status    chat_response
                                        (思考中...)     (最终回复)
                                              │             │
                                              ▼             ▼
                                           WebSocket ──► Godot
```

### Architecture Principles

- **依赖倒置**: Agent Core 不直接依赖具体 LLM 提供商，通过 `LLMClient` 接口抽象
- **可观测性**: 每个 ReAct 步骤都通过 WebSocket 通知前端，便于调试和用户感知
- **工具解耦**: 本阶段 Agent 仅定义工具调用的接口格式，实际工具在 Phase 04 注册

### Out of scope

- 实际工具的实现与注册 (Phase 04)
- 屏幕视觉能力 (Phase 05)
- 流式响应输出 (可在后续迭代中追加)
- 多轮对话的持久化存储 (关闭程序后历史丢失，V1.0 考虑)

## §4 Interface Contract

### LLM 客户端

```python
# server/lumina/agent/llm_client.py
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class ChatMessage:
    role: str              # "system" | "user" | "assistant" | "tool"
    content: str | None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None
    name: str | None = None


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict       # JSON Schema


@dataclass
class LLMResponse:
    message: ChatMessage
    usage: dict | None = None  # {"prompt_tokens": ..., "completion_tokens": ...}
    finish_reason: str = "stop"


class LLMClient:
    def __init__(
        self,
        api_base: str,
        api_key: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> None: ...

    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[ToolDefinition] | None = None,
    ) -> LLMResponse:
        """发送聊天请求，返回模型响应。支持 Function Calling。"""
        ...
```

### Agent 核心

```python
# server/lumina/agent/core.py
from typing import Callable, Awaitable


class AgentCore:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str,
        max_iterations: int = 10,
        history_window: int = 20,
    ) -> None: ...

    async def process_message(self, user_text: str) -> str:
        """处理用户消息，执行 ReAct 循环，返回最终回复文本。"""
        ...

    def register_tool(self, tool: ToolDefinition, handler: Callable[..., Awaitable[str]]) -> None:
        """注册一个可被 Agent 调用的工具。"""
        ...

    def get_conversation_history(self) -> list[ChatMessage]:
        """获取当前对话历史。"""
        ...

    def clear_history(self) -> None:
        """清空对话历史（保留系统提示词）。"""
        ...

    def set_system_prompt(self, prompt: str) -> None:
        """更新系统提示词 / 角色人设。"""
        ...


# server/lumina/agent/react_loop.py

class ReActLoop:
    """单次用户请求的 ReAct 推理循环。"""

    def __init__(
        self,
        llm_client: LLMClient,
        messages: list[ChatMessage],
        tools: dict[str, tuple[ToolDefinition, Callable]],
        max_iterations: int = 10,
        on_status: Callable[[str, str], Awaitable[None]] | None = None,
    ) -> None: ...

    async def run(self) -> str:
        """执行循环直到获得最终回复或达到最大迭代次数。"""
        ...
```

### 配置扩展

```python
# server/lumina/config.py (扩展)
from dataclasses import dataclass, field


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
    models: list[ModelConfig] = field(default_factory=list)
    active_model: str = "glm-4-flash"
    agent: AgentConfig = field(default_factory=AgentConfig)
```

### WebSocket 集成

```python
# server/lumina/__main__.py 中的消息处理 (伪代码)

async def on_user_message(msg: Message) -> None:
    # 通知前端 Agent 开始思考
    await ws_server.send(Message(
        type=MessageType.AGENT_STATUS,
        payload={"status": "thinking", "message": "正在思考..."}
    ))

    # 更新桌宠状态为思考中
    await ws_server.send(Message(
        type=MessageType.PET_COMMAND,
        payload={"command": "set_state", "data": {"state": "thinking"}}
    ))

    # 执行 ReAct 循环
    reply = await agent.process_message(msg.payload["text"])

    # 发送回复
    await ws_server.send(Message(
        type=MessageType.CHAT_RESPONSE,
        payload={"text": reply, "streaming": False, "done": True}
    ))

    # 桌宠回到待机
    await ws_server.send(Message(
        type=MessageType.PET_COMMAND,
        payload={"command": "set_state", "data": {"state": "idle"}}
    ))
```

## §5 Implementation Steps

1. **安装依赖**: 在 `pyproject.toml` 中添加 `httpx` (HTTP 客户端)。
2. **实现 LLM 客户端** (`server/lumina/agent/llm_client.py`): 封装 OpenAI 兼容 API 调用，支持普通聊天和 Function Calling。使用 `httpx.AsyncClient`。
3. **实现数据模型** (`server/lumina/agent/llm_client.py`): `ChatMessage`, `ToolDefinition`, `LLMResponse` 数据类。
4. **实现 ReAct 循环** (`server/lumina/agent/react_loop.py`): 核心推理循环，包含迭代控制、工具调用分发和状态回调。
5. **实现 Agent Core** (`server/lumina/agent/core.py`): 封装 LLM 客户端 + ReAct 循环 + 对话历史管理 + 工具注册。
6. **扩展配置模块** (`server/lumina/config.py`): 添加 `ModelConfig` 和 `AgentConfig`。
7. **集成到 WebSocket 服务**: 修改 `__main__.py`，将 `user_message` 路由到 `AgentCore.process_message()`，并通过 WebSocket 广播状态更新。
8. **使用 GLM-4-Flash 测试**: 配置 GLM API Key，发送测试对话验证 ReAct 循环正常工作。
9. **编写单元测试** (`server/tests/test_agent.py`): 测试 LLM 客户端 mock、ReAct 循环逻辑、对话历史裁剪。

## §6 Acceptance Criteria

- [ ] `LLMClient` 能成功调用 GLM-4-Flash API 并返回响应
- [ ] ReAct 循环在无工具可用时直接返回对话回复
- [ ] ReAct 循环在注册了 mock 工具时能正确解析 `tool_calls` 并调用处理函数
- [ ] 循环次数超过 `max_iterations` 时安全终止并返回提示信息
- [ ] 对话历史正确维护，超过 `history_window` 时自动裁剪旧消息
- [ ] 每次 Thought 步骤通过 WebSocket 发送 `agent_status` 到 Godot 端
- [ ] `pytest server/tests/test_agent.py` 全部通过
- [ ] 端到端: 从 Godot 发送文字消息，经 Agent 处理后收到回复，桌宠经历 thinking → idle 状态变化

## §7 State Teardown Checklist

- [ ] **Phase Document Updated** (if design changed during implementation)
- [ ] `changelog.md` updated
- [ ] `api_registry/agent_core.md` updated
- [ ] `master_overview.md` Phase 03 status set to `[x] Done`
