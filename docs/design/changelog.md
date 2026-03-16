# Changelog — Lumina

## [0.3.0] - 2026-03-15 — Phase 05 — 视觉智能与交互链路

### Delivered
- **三级感知策略 (Perception Tiering)**: 实现 UI Automation (Tier 1) -> OCR (Tier 2) -> AI 视觉分析 (Tier 3) 的分层感知逻辑。
- **活动窗口管理**: 实现 `WindowManager` 负责窗口查找、激活和 `WindowRect` 坐标获取。
- **比例坐标转换**: 实现 `CoordinateConverter` 在相对窗口比例坐标 (0.0~1.0) 与屏幕绝对像素间双向转换。
- **UI Automation (Tier 1)**: 基于 `uiautomation` 扫描窗口元素树并序列化为 AI 可读文本。
- **OCR 识别 (Tier 2)**: 集成 `EasyOCR` 实现窗口区域文字识别与定位（替代环境不稳定的 PaddleOCR）。
- **AI 视觉分析 (Tier 3)**: 实现基于多模态 LLM 的截图定位功能作为兜底。
- **物理交互模拟**: 封装 `pyautogui` 实现平滑移动、点击、双击、右键、拖拽、文本输入和快捷键。
- **视觉工具集**: 新增 `inspect_window`, `visual_locate`, `click_at`, `type_text`, `hotkey` 并注册到 Agent。
- **交互链路闭环**: 实现"桌宠跑过去点击"完整链路，支持 Godot 状态回调 (`click_ready`) 触发物理操作。
- **Godot 扩展**: 新增 `Observing` 和 `Clicking` 状态，支持 `perform_click` 指令和 `pet_event` 回馈。

### Decisions
- **OCR 引擎切换**: 因 PaddlePaddle 3.0 在当前 Windows/Python 3.12 环境下存在 oneDNN 兼容性问题，切换为更稳定的 `EasyOCR`。
- **异步点击协调**: `ClickAtTool` 采用 `asyncio.Event` 监听 WebSocket 回传的 `pet_event:click_ready`，确保物理点击与动画同步。
- **延迟加载策略**: OCR 模型和 UIA 扫描器仅在首次调用时初始化，减少服务启动开销。

---

## 2026-03-15 — Phase 04 补充：用户交互工具

### Delivered
- 在 `phase_04_tool_system.md` 中新增 `ask_user` 和 `notify_user` 工具定义
- 更新 `api_registry/tool_system.md` 新增用户交互工具分类
- 更新 `api_registry/websocket_protocol.md` 新增 `user_prompt` / `user_prompt_response` 消息

### Decisions
- `ask_user` 支持两种输入模式: 自由文本 (`text`) 和选择题 (`choice`)
- 提问超时默认 120s，超时后返回 "用户未回复" 给 Agent，Agent 自行决定后续行为
- `notify_user` 为非阻塞通知，通过 `show_bubble` pet_command 实现
- 交互工具需要 WebSocket 服务实例引用，构造时注入 `ws_server`

---

## 2026-03-15 — Phase 05 设计重构：三级感知策略

### Delivered
- 重写 `phase_05_screen_vision.md`，用三级感知策略替换原方案
- 更新 `api_registry/tool_system.md` 中的视觉工具和支撑模块

### Decisions
- **三级感知策略**: Tier 1 UI Automation (最快/最准/零成本) → Tier 2 OCR 文本提取 (快速/低成本) → Tier 3 AI 视觉分析 (兜底/高成本)
- **活动窗口聚焦**: 不做全屏截图，仅截取目标应用活动窗口区域，减少信息噪声和 token 开销
- **比例坐标系**: AI 统一返回 (rx, ry) 比例值 (0.0~1.0)，系统根据窗口实际位置/尺寸换算为屏幕绝对像素，解决截图缩放与分辨率不一致问题
- **OCR 数据先序列化再推理**: OCR 结果序列化为纯文本发给 AI 进行逻辑推理，而非依赖 AI 视觉能力直接看截图
- **Tier 3 仅为兜底**: 仅当 UIA 和 OCR 均无法定位目标 (如图标、无标签控件) 时，才发送缩放后的窗口截图给 AI
- **工具重构**: 原 `capture_screen` + `find_and_click` 合并重构为 `inspect_window` + `visual_locate` + `click_at`(比例坐标)
- **新增支撑模块**: `WindowManager`, `CoordinateConverter`, `UIAutomationScanner`, `AIVisualAnalyzer`, `WindowPerceiver`

### Deferred
- macOS/Linux 平台的 UIA 替代方案 (macOS: NSAccessibility, Linux: AT-SPI) 留待 Phase 08

---

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
