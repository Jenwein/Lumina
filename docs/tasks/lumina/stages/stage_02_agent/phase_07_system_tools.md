# Phase 07: 系统工具 - 文件操作

## §1 Goal
实现文件管理 (CRUD)、应用启动/关闭、系统状态监测的工具集，注册到 Agent ToolRegistry。

## §2 Dependencies
- **Prerequisite phases**: Phase 06
- **Source files to read**: `server/src/lumina/agent/tool_registry.py`, `server/src/lumina/tools/`

## §3 Design & Constraints
- **Architecture principles**:
  - 文件工具：read_file、write_file、list_directory、delete_file、move_file、copy_file
  - 应用工具：launch_app、close_app（按 PID 或进程名）、list_processes
  - 系统工具：system_status（CPU、内存、磁盘）
  - 所有工具均为 async 函数，返回 ToolResult
  - 路径安全校验：阻止目录遍历攻击，限制在可配置根目录内操作
  - 使用 pathlib 实现跨平台路径处理，psutil 获取进程/系统信息
- **Boundary conditions**:
  - 文件操作限定在配置的根目录内，任何 `../` 遍历尝试均被拒绝
  - 文件读取大小限制（默认 10MB），超限返回错误
  - launch_app 仅允许配置中的白名单命令（安全策略）
  - close_app 不允许关闭系统关键进程
- **Out of scope**: 网页自动化（Phase 09+）、屏幕交互、文件监听

## §4 Interface Contract

### 文件工具

```python
# server/src/lumina/tools/file_tools.py
from lumina.agent.tool_registry import ToolResult

async def read_file(path: str) -> ToolResult: ...
async def write_file(path: str, content: str) -> ToolResult: ...
async def list_directory(path: str, recursive: bool = False) -> ToolResult: ...
async def delete_file(path: str) -> ToolResult: ...
async def move_file(src: str, dst: str) -> ToolResult: ...
async def copy_file(src: str, dst: str) -> ToolResult: ...
```

### 应用工具

```python
# server/src/lumina/tools/app_tools.py
from lumina.agent.tool_registry import ToolResult

async def launch_app(command: str, args: list[str] = []) -> ToolResult: ...
async def close_app(pid: int | None = None, name: str | None = None) -> ToolResult: ...
async def list_processes(filter_name: str | None = None) -> ToolResult: ...
```

### 系统工具

```python
# server/src/lumina/tools/system_tools.py
from lumina.agent.tool_registry import ToolResult

async def system_status() -> ToolResult: ...
```

### 批量注册

```python
# server/src/lumina/tools/registry.py
from lumina.agent.tool_registry import ToolRegistry

def register_all_tools(registry: ToolRegistry) -> None: ...
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/tools/file_tools.py` — 文件 CRUD 操作，包含路径安全校验（阻止目录遍历）
2. 创建 `server/src/lumina/tools/app_tools.py` — 通过 psutil/subprocess 管理进程
3. 创建 `server/src/lumina/tools/system_tools.py` — 通过 psutil 获取系统信息
4. 创建 `server/src/lumina/tools/registry.py` — 批量注册辅助函数，将所有工具注册到 ToolRegistry
5. 在 `server/pyproject.toml` 中添加 psutil 依赖
6. 创建 `server/tests/test_tools.py` — 使用临时目录/文件测试每个工具

## §6 Acceptance Criteria
- [ ] 文件工具：read、write、list、delete、move、copy 均在临时文件系统上正确工作
- [ ] 路径安全校验：阻止 `../../../etc/passwd` 等目录遍历攻击
- [ ] 应用工具：可启动一个进程、列出该进程、然后关闭它
- [ ] system_status 返回 CPU 使用率、内存使用率、磁盘使用量
- [ ] 所有工具通过 `register_all_tools()` 成功注册到 ToolRegistry
- [ ] 每个工具的 JSON Schema 参数定义正确，可被 LLM function calling 使用
- [ ] 所有测试通过：`uv run pytest server/tests/test_tools.py`

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
