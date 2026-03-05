# Phase 05: LLM 集成层

## §1 Goal
实现兼容 OpenAI 格式的多模型 LLM 客户端，支持流式响应和多 API 节点配置切换。

## §2 Dependencies
- **Prerequisite phases**: Phase 01
- **Source files to read**: `server/src/lumina/llm/`, `server/src/lumina/config/`

## §3 Design & Constraints
- **Architecture principles**:
  - 使用 httpx 或 openai SDK 发送 HTTP 请求到 OpenAI 兼容端点
  - 支持多模型：GPT-4、Claude（通过兼容代理）、DeepSeek、Ollama 本地模型
  - 通过 SSE（Server-Sent Events）/ async iterator 实现流式响应
  - 配置方式：YAML 配置文件 + 环境变量覆盖
  - 多 Provider 管理，支持运行时切换
- **Boundary conditions**:
  - API Key 不得硬编码，必须通过配置文件或环境变量注入
  - 流式和非流式均返回统一的数据结构
  - 网络超时默认 30 秒，可配置
  - 错误处理：API 错误、网络超时、速率限制均需优雅处理
- **Out of scope**: Agent 逻辑、工具调用编排、Prompt 工程

## §4 Interface Contract

### 数据模型

```python
# server/src/lumina/llm/models.py
from pydantic import BaseModel
from typing import Literal, AsyncIterator

class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None

class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: FunctionCall

class FunctionCall(BaseModel):
    name: str
    arguments: str  # JSON string

class LLMConfig(BaseModel):
    name: str
    api_base: str
    api_key: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7

class ChatResponse(BaseModel):
    content: str
    tool_calls: list[ToolCall] | None = None
    usage: dict | None = None

class ChatChunk(BaseModel):
    delta_content: str | None = None
    delta_tool_calls: list[ToolCall] | None = None
    finish_reason: str | None = None
```

### LLM 客户端

```python
# server/src/lumina/llm/client.py
class LLMClient:
    def __init__(self, config: LLMConfig): ...
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        stream: bool = False,
    ) -> ChatResponse: ...
    async def chat_stream(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatChunk]: ...
```

### Provider 管理器

```python
# server/src/lumina/llm/manager.py
class LLMManager:
    def __init__(self, config_path: str): ...
    def load_config(self) -> None: ...
    def add_provider(self, config: LLMConfig) -> None: ...
    def switch_provider(self, name: str) -> None: ...
    def get_client(self) -> LLMClient: ...
    def list_providers(self) -> list[str]: ...
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/llm/models.py` — 定义 Message、ToolCall、FunctionCall、LLMConfig、ChatResponse、ChatChunk
2. 创建 `server/src/lumina/llm/client.py` — 基于 httpx async 的 LLMClient，支持流式/非流式
3. 创建 `server/src/lumina/llm/manager.py` — LLMManager 多 Provider 管理与切换
4. 创建 `server/src/lumina/config/settings.py` — 全局配置加载器（YAML + 环境变量）
5. 创建 `server/config.example.yaml` — 示例配置文件（含多个 Provider 配置模板）
6. 创建 `server/tests/test_llm.py` — 使用 mock API 响应的单元测试

## §6 Acceptance Criteria
- [ ] LLMClient 可对 mock 端点发起非流式 chat 调用并获取 ChatResponse
- [ ] LLMClient 可对 mock 端点发起流式 chat 调用并逐块迭代 ChatChunk
- [ ] LLMManager 从 YAML 加载配置，支持在多个 Provider 之间切换
- [ ] 支持 tool_calls 格式（OpenAI function calling 兼容）
- [ ] API Key 通过环境变量覆盖配置文件中的值
- [ ] 所有测试通过：`uv run pytest server/tests/test_llm.py`

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
