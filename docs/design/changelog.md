# Changelog — Lumina

## 2026-03-14 — 初始化：设计文档体系搭建

### Delivered
- 创建完整的设计文档目录结构 (`docs/design/`)
- 编写 `master_overview.md` 作为项目唯一入口 (SSOT)
- 将项目拆解为 8 个阶段，分属 5 个 Stage，对齐 PRD 里程碑
- 初始化 `api_registry/` 四个模块接口文件骨架
- 编写全部 8 个阶段文档，定义接口契约和验收标准

### Decisions
- 采用 C/S 架构：Python 后端 (Logic Server) + Godot 前端 (Display Client)
- 通信协议选择 WebSocket + JSON，默认端口 8765
- Python 端采用 asyncio 异步架构
- Godot 端使用 GDScript，目标引擎版本 4.6.1
- LLM 集成统一使用 OpenAI 兼容 API 格式
- GLM-4-Flash 作为开发测试用模型
- 安全机制采用"高危操作拦截 + 用户物理确认"模式

### Deferred
- 具体的 2D 角色美术资源设计
- Spine/Live2D/VRM 等高级模型资产方案的技术选型细节
- CI/CD 流水线与自动化测试框架的具体配置
- 国际化 (i18n) 方案

## [0.2.1] - 2026-03-15

### Added
- **Tool System (Phase 04)**: Implemented a scalable tool registration and discovery framework.
- **Base Components**: Created `BaseTool` and `ToolRegistry` with risk level management (LOW/MEDIUM/HIGH).
- **File Tools**: Added `read_file`, `write_file`, `list_directory`, `create_directory`, `delete_file`, and `move_file`.
- **Application Tools**: Added `launch_app` (async subprocess) and `close_app` (psutil-based).
- **System Tools**: Added `get_system_info` and `get_running_processes`.
- **Integration**: Registered all tools to `AgentCore` in `server/lumina/__main__.py`.
- **Tests**: Added comprehensive unit tests in `server/tests/test_tools.py` for all tool operations and the registry.
- **Dependencies**: Added `psutil` and `aiofiles` to `pyproject.toml`.

## [0.2.0] - 2026-03-15

### Added
- 实现 Agent 决策引擎 (Phase 03)
- `LLMClient` 支持 OpenAI 兼容 API 和 Function Calling
- `ReActLoop` 实现基于 ReAct 模式的自主推理循环
- `AgentCore` 负责对话历史管理、工具注册与状态回调
- WebSocket 服务集成 Agent 推理，支持实时状态更新 (`agent_status`)
- 单元测试 `server/tests/test_agent.py` 验证核心逻辑
- 扩展配置支持多模型切换和 Agent 参数设置

### Added
- **Project Structure**: Initialized `server/` (Python) and `client/` (Godot) directories.
- **WebSocket Protocol**: Implemented a JSON-based bidirectional communication protocol for Python-Godot interaction.
- **Python Server**: Asyncio-based WebSocket server with single-client locking and heartbeat support.
- **Godot Client**: Robust `LuminaWSClient` with automatic reconnection and handshake handling.
- **Integration Tests**: Automated tests for connection handshake, heartbeat, and multiple client rejection.

## [0.2.0] - 2026-03-14

### Added
- **Godot Pet Layer**: Implemented `PetController` for handling movement and state transitions.
- **State Machine**: Built a generic `PetStateMachine` with `Idle`, `Walking`, `Thinking`, and `Typing` states.
- **Window Management**: Implemented `WindowManager` for transparent, borderless, always-on-top windowing with dynamic mouse passthrough regions.
- **WebSocket Integration**: Connected Godot Pet to Python Server via `pet_command` protocol (`move_to`, `set_state`).
- **End-to-End Tests**: Verified the full loop from Python command to Godot animation/movement.
- **Asset Placeholder**: Integrated `PlaceholderTexture2D` for rapid prototyping without external assets.

---

*(Append new entries above this line)*
