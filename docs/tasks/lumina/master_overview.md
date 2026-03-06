# Task: Lumina — Interactive AI Desktop Pet Agent

## Meta
- **Created**: 2026-03-05
- **Last Updated**: 2026-03-07
- **Status**: In Progress
- **Complexity**: High

## Documentation Index
- **GodotDocs**: [GodotDocs](../../godot-docs/)
- **Changelog**: [changelog.md](./changelog.md)
- **API Registry**: [Index](./api_registry/)
  - [Core](./api_registry/core.md)
  - [Tools](./api_registry/tools.md)
  - [UI](./api_registry/ui.md)

## Objective
构建一个将 LLM 推理能力与 Godot 渲染桌面宠物相结合的交互式 AI Agent 桌面应用。通过 Python 后端实现 ReAct 自主循环、工具调用、屏幕感知，通过 Godot 前端实现透明置顶桌宠、动画状态机、对话气泡，两端经由 WebSocket 通信，最终交付一个既具备强大办公/操作能力，又具有情感价值 and 视觉反馈的桌面助手。

## Constraints & Architecture Decisions
- **架构模式**: Client-Server — Python 后端 (uv + FastAPI) 为逻辑服务器，Godot 4.x 前端为显示客户端
- **通信协议**: 本地 WebSocket，JSON 序列化指令，端口可配置
- **OCR 方案**: PaddleOCR (本地，中文支持佳) + LLM 多模态视觉辅助
- **LLM 兼容性**: 支持所有 OpenAI 格式 API（GPT-4, Claude, DeepSeek, Ollama 等）
- **V0.1 素材策略**: 占位图形/几何形状，后续迭代至 SpriteSheet → Spine/Live2D → VRM 3D
- **跨平台目标**: Windows (原生)、macOS (沙盒权限引导)、Linux (X11 + Wayland)
- **安全原则**: 高危操作必须物理确认，支持单步执行模式
- **隐私原则**: 黑名单应用自动禁用截图，支持隐私遮罩区域

## Phase Map

### Stage 1: Foundation Infrastructure (V0.1)

| Phase | Title | Status | Dependencies | File |
|-------|-------|--------|--------------|------|
| 01 | 项目脚手架与环境搭建 | [ ] Pending | — | [phase_01.md](./stages/stage_01_foundation/phase_01_scaffolding.md) |
| 02 | WebSocket 通信协议 | [ ] Pending | Phase 01 | [phase_02.md](./stages/stage_01_foundation/phase_02_websocket.md) |
| 03 | Godot 桌宠窗口 | [ ] Pending | Phase 01 | [phase_03.md](./stages/stage_01_foundation/phase_03_pet_window.md) |
| 04 | 运动与指令系统 | [ ] Pending | Phase 02, 03 | [phase_04.md](./stages/stage_01_foundation/phase_04_movement.md) |

### Stage 2: Agent Intelligence (V0.2)

| Phase | Title | Status | Dependencies | File |
|-------|-------|--------|--------------|------|
| 05 | LLM 集成层 | [ ] Pending | Phase 01 | [phase_05.md](./stages/stage_02_agent/phase_05_llm_integration.md) |
| 06 | ReAct 自主循环 | [ ] Pending | Phase 05 | [phase_06.md](./stages/stage_02_agent/phase_06_react_loop.md) |
| 07 | 系统工具 - 文件操作 | [ ] Pending | Phase 06 | [phase_07.md](./stages/stage_02_agent/phase_07_system_tools.md) |
| 08 | 对话气泡 UI | [ ] Pending | Phase 04, 06 | [phase_08.md](./stages/stage_02_agent/phase_08_dialogue_ui.md) |

### Stage 3: Vision & Automation (V0.3)

| Phase | Title | Status | Dependencies | File |
|-------|-------|--------|--------------|------|
| 09 | 屏幕截取系统 | [ ] Pending | Phase 01 | [phase_09.md](./stages/stage_03_vision/phase_09_screen_capture.md) |
| 10 | OCR 与视觉分析 | [ ] Pending | Phase 09 | [phase_10.md](./stages/stage_03_vision/phase_10_ocr.md) |
| 11 | 输入模拟工具 | [ ] Pending | Phase 06 | [phase_11.md](./stages/stage_03_vision/phase_11_input_simulation.md) |
| 12 | 视觉交互全链路 | [ ] Pending | Phase 04, 10, 11 | [phase_12.md](./stages/stage_03_vision/phase_12_visual_chain.md) |

### Stage 4: Platform & Configuration (V0.4)

| Phase | Title | Status | Dependencies | File |
|-------|-------|--------|--------------|------|
| 13 | 多显示器支持 | [ ] Pending | Phase 09, 04 | [phase_13.md](./stages/stage_04_platform/phase_13_multi_monitor.md) |
| 14 | 配置界面 | [ ] Pending | Phase 05, 08 | [phase_14.md](./stages/stage_04_platform/phase_14_config_ui.md) |
| 15 | 跨平台适配 | [ ] Pending | Phase 09, 03 | [phase_15.md](./stages/stage_04_platform/phase_15_cross_platform.md) |

### Stage 5: Release Readiness (V1.0)

| Phase | Title | Status | Dependencies | File |
|-------|-------|--------|--------------|------|
| 16 | 安全与确认机制 | [ ] Pending | Phase 06, 08 | [phase_16.md](./stages/stage_05_release/phase_16_safety.md) |
| 17 | 隐私保护 | [ ] Pending | Phase 09, 16 | [phase_17.md](./stages/stage_05_release/phase_17_privacy.md) |
| 18 | 动画状态机完善 | [ ] Pending | Phase 04, 12 | [phase_18.md](./stages/stage_05_release/phase_18_animations.md) |
| 19 | 资源优化与打包 | [ ] Pending | All prior | [phase_19.md](./stages/stage_05_release/phase_19_optimization.md) |

## Notes
- Godot 前端使用 GDScript 2.0，Python 后端使用 async/await 异步模式
- PaddleOCR 仅在 Agent 无法通过常规 API 获取信息时触发（按需 OCR）
- 模型资产按阶段迭代：占位图 → SpriteSheet → Spine/Live2D → VRM 3D
- WebSocket 消息协议需版本化，为未来扩展留空间
