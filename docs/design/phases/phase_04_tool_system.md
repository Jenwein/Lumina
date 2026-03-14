# Phase 04: 工具系统

## §1 Goal

构建可扩展的工具注册与发现框架，实现首批系统控制工具（文件管理、应用启动/关闭、系统状态监测），使 Agent 能通过 ReAct 循环自动调用这些工具来完成用户的操作请求。

## §2 Dependencies

- **Prerequisite phases**: Phase 03 (`[x] Done`)
- **Reference Materials**:
    - [x] [PRD — 工具系统](../../../PRD.md) §2.2
    - [x] [OpenAI Function Calling 规范](https://platform.openai.com/docs/guides/function-calling)
- **Source files to read**:
    - [x] `server/lumina/agent/core.py` (Phase 03 — `register_tool` 接口)
    - [x] `server/lumina/agent/llm_client.py` (Phase 03 — `ToolDefinition`)
    - [x] `server/lumina/agent/react_loop.py` (Phase 03 — 工具调用分发)

## §3 Design & Constraints

### 工具框架设计

采用装饰器 + 自动注册模式，每个工具是一个独立的 Python 类：

```
server/lumina/tools/
├── __init__.py
├── base.py                 # 工具基类与注册器
├── registry.py             # 工具注册表
├── file_tools.py           # 文件管理工具集
├── app_tools.py            # 应用控制工具集
└── system_tools.py         # 系统状态工具集
```

**设计原则**:
- 每个工具类继承 `BaseTool`，声明 `name`, `description`, `parameters` (JSON Schema)
- 工具通过 `ToolRegistry` 统一管理，自动生成 `ToolDefinition` 列表供 LLM 使用
- 工具方法为 async，返回字符串结果（成功信息或错误描述）
- 高危工具标记 `risk_level`，由安全层拦截（Phase 07 实现拦截逻辑，本阶段仅标记）

### 本阶段实现的工具

| 工具名称 | 功能 | 风险等级 | 参数 |
|---------|------|---------|------|
| `read_file` | 读取文件内容 | low | `path: str` |
| `write_file` | 写入文件内容 | medium | `path: str, content: str` |
| `list_directory` | 列出目录内容 | low | `path: str` |
| `create_directory` | 创建目录 | low | `path: str` |
| `delete_file` | 删除文件 | high | `path: str` |
| `move_file` | 移动/重命名文件 | medium | `src: str, dst: str` |
| `launch_app` | 启动应用程序 | medium | `command: str, args: list[str]` |
| `close_app` | 关闭应用程序 | medium | `process_name: str` |
| `get_system_info` | 获取系统信息 | low | 无 |
| `get_running_processes` | 获取进程列表 | low | `filter: str \| None` |

### 工具执行流程

```
Agent ReAct Loop
       │
       │ tool_calls: [{"name": "read_file", "arguments": {"path": "..."}}]
       │
       ▼
ToolRegistry.execute(name, arguments)
       │
       ├── 查找工具 → 未找到 → 返回错误信息
       │
       ├── 检查风险等级 → high → (Phase 07: 发送确认请求)
       │                          本阶段: 打印警告并执行
       │
       └── 调用 tool.execute(**arguments)
              │
              ├── 成功 → 返回结果字符串
              └── 异常 → 捕获并返回错误描述
```

### Architecture Principles

- **沙箱意识**: 文件操作默认限制在用户主目录下（可配置白名单路径）
- **幂等描述**: 工具的 `description` 必须清晰描述副作用，帮助 LLM 正确选择
- **错误友好**: 工具返回的错误信息应对 LLM 友好（自然语言描述而非堆栈跟踪）
- **异步执行**: 所有工具方法为 async，支持 I/O 密集操作

### Out of scope

- 屏幕截图 / OCR / 点击模拟 (Phase 05)
- Web 浏览器操作 (Phase 06)
- 高危操作的用户确认流程 (Phase 07, 本阶段仅标记风险等级)

## §4 Interface Contract

```python
# server/lumina/tools/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BaseTool(ABC):
    name: str
    description: str
    parameters: dict          # JSON Schema for arguments
    risk_level: RiskLevel = RiskLevel.LOW

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """执行工具操作，返回结果描述字符串。"""
        ...

    def to_tool_definition(self) -> "ToolDefinition":
        """转换为 LLM ToolDefinition 格式。"""
        ...


# server/lumina/tools/registry.py
class ToolRegistry:
    def __init__(self) -> None: ...

    def register(self, tool: BaseTool) -> None:
        """注册一个工具实例。"""
        ...

    def get(self, name: str) -> BaseTool | None:
        """按名称获取工具。"""
        ...

    def list_definitions(self) -> list["ToolDefinition"]:
        """获取所有已注册工具的 ToolDefinition 列表（传给 LLM）。"""
        ...

    async def execute(self, name: str, arguments: dict) -> str:
        """查找并执行指定工具，返回结果。"""
        ...


# server/lumina/tools/file_tools.py
class ReadFileTool(BaseTool):
    name = "read_file"
    description = "读取指定路径文件的文本内容。适用于查看配置文件、日志等。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件的绝对路径或相对路径"}
        },
        "required": ["path"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, path: str) -> str: ...


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "将内容写入指定文件。如果文件不存在则创建，存在则覆盖。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目标文件路径"},
            "content": {"type": "string", "description": "要写入的文本内容"}
        },
        "required": ["path", "content"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, path: str, content: str) -> str: ...


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "永久删除指定路径的文件。此操作不可撤销。"
    risk_level = RiskLevel.HIGH
    # ... parameters 略


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "列出指定目录下的文件和子目录。"
    risk_level = RiskLevel.LOW
    # ... parameters 略


class CreateDirectoryTool(BaseTool):
    name = "create_directory"
    description = "创建目录，支持递归创建中间目录。"
    risk_level = RiskLevel.LOW
    # ... parameters 略


class MoveFileTool(BaseTool):
    name = "move_file"
    description = "移动或重命名文件/目录。"
    risk_level = RiskLevel.MEDIUM
    # ... parameters 略


# server/lumina/tools/app_tools.py
class LaunchAppTool(BaseTool):
    name = "launch_app"
    description = "启动一个应用程序或执行一个命令。"
    risk_level = RiskLevel.MEDIUM

    async def execute(self, command: str, args: list[str] | None = None) -> str: ...


class CloseAppTool(BaseTool):
    name = "close_app"
    description = "关闭指定名称的应用程序进程。"
    risk_level = RiskLevel.MEDIUM

    async def execute(self, process_name: str) -> str: ...


# server/lumina/tools/system_tools.py
class GetSystemInfoTool(BaseTool):
    name = "get_system_info"
    description = "获取当前系统信息，包括操作系统、CPU、内存、磁盘等。"
    risk_level = RiskLevel.LOW

    async def execute(self) -> str: ...


class GetRunningProcessesTool(BaseTool):
    name = "get_running_processes"
    description = "获取当前运行的进程列表，可选按名称过滤。"
    risk_level = RiskLevel.LOW

    async def execute(self, filter: str | None = None) -> str: ...
```

### Agent Core 集成

```python
# server/lumina/__main__.py 启动时的工具注册 (伪代码)

registry = ToolRegistry()
registry.register(ReadFileTool())
registry.register(WriteFileTool())
registry.register(DeleteFileTool())
registry.register(ListDirectoryTool())
registry.register(LaunchAppTool())
registry.register(CloseAppTool())
registry.register(GetSystemInfoTool())
registry.register(GetRunningProcessesTool())

agent = AgentCore(
    llm_client=llm_client,
    system_prompt=config.agent.system_prompt,
)

for tool in registry.tools.values():
    agent.register_tool(
        tool.to_tool_definition(),
        tool.execute
    )
```

## §5 Implementation Steps

1. **实现工具基类** (`server/lumina/tools/base.py`): `BaseTool` 抽象类与 `RiskLevel` 枚举。
2. **实现工具注册表** (`server/lumina/tools/registry.py`): `ToolRegistry`，支持注册、查找、列表和执行。
3. **实现文件工具集** (`server/lumina/tools/file_tools.py`): `ReadFileTool`, `WriteFileTool`, `DeleteFileTool`, `ListDirectoryTool`, `CreateDirectoryTool`, `MoveFileTool`。
4. **实现应用控制工具** (`server/lumina/tools/app_tools.py`): `LaunchAppTool` (使用 `asyncio.create_subprocess_exec`), `CloseAppTool` (使用 `psutil`)。
5. **实现系统状态工具** (`server/lumina/tools/system_tools.py`): `GetSystemInfoTool`, `GetRunningProcessesTool` (使用 `platform` + `psutil`)。
6. **集成到 Agent**: 修改 `__main__.py`，启动时注册所有工具到 `AgentCore`。
7. **更新依赖**: 在 `pyproject.toml` 中添加 `psutil`。
8. **编写测试** (`server/tests/test_tools.py`): 每个工具的单元测试，包括正常执行和错误处理。
9. **端到端验证**: 通过 Godot 发送 "列出桌面文件"，验证 Agent 自动调用 `list_directory` 并返回结果。

## §6 Acceptance Criteria

- [x] `ToolRegistry` 能正确注册和发现所有工具
- [x] `list_definitions()` 返回的格式与 OpenAI Function Calling 兼容
- [x] `read_file` 能读取存在的文件，不存在时返回友好错误信息
- [x] `write_file` 能创建和覆盖文件
- [x] `delete_file` 标记为 HIGH 风险等级
- [x] `launch_app` 能启动 notepad 等简单应用
- [x] `get_system_info` 返回包含 OS、CPU、内存信息的格式化字符串
- [x] Agent 能在对话中自动选择正确的工具（通过 GLM-4-Flash 测试）
- [x] `pytest server/tests/test_tools.py` 全部通过

## §7 State Teardown Checklist

- [x] **Phase Document Updated** (if design changed during implementation)
- [x] `changelog.md` updated
- [x] `api_registry/tool_system.md` updated
- [x] `master_overview.md` Phase 04 status set to `[x] Done`
