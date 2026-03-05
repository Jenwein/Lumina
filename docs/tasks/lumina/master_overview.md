# Task: Lumina — Interactive AI Desktop Pet Agent

## Meta
- **Created**: 2026-03-05
- **Last Updated**: 2026-03-05
- **Status**: In Progress
- **Complexity**: High

## Objective
构建一个将 LLM 推理能力与 Godot 渲染桌面宠物相结合的交互式 AI Agent 桌面应用。通过 Python 后端实现 ReAct 自主循环、工具调用、屏幕感知，通过 Godot 前端实现透明置顶桌宠、动画状态机、对话气泡，两端经由 WebSocket 通信，最终交付一个既具备强大办公/操作能力，又具有情感价值和视觉反馈的桌面助手。

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

| Phase | Title | Status | Dependencies |
|-------|-------|--------|--------------|
| 01 | 项目脚手架与环境搭建 | [ ] Pending | — |
| 02 | WebSocket 通信协议 | [ ] Pending | Phase 01 |
| 03 | Godot 桌宠窗口 | [ ] Pending | Phase 01 |
| 04 | 运动与指令系统 | [ ] Pending | Phase 02, 03 |

### Stage 2: Agent Intelligence (V0.2)

| Phase | Title | Status | Dependencies |
|-------|-------|--------|--------------|
| 05 | LLM 集成层 | [ ] Pending | Phase 01 |
| 06 | ReAct 自主循环 | [ ] Pending | Phase 05 |
| 07 | 系统工具 - 文件操作 | [ ] Pending | Phase 06 |
| 08 | 对话气泡 UI | [ ] Pending | Phase 04, 06 |

### Stage 3: Vision & Automation (V0.3)

| Phase | Title | Status | Dependencies |
|-------|-------|--------|--------------|
| 09 | 屏幕截取系统 | [ ] Pending | Phase 01 |
| 10 | OCR 与视觉分析 | [ ] Pending | Phase 09 |
| 11 | 输入模拟工具 | [ ] Pending | Phase 06 |
| 12 | 视觉交互全链路 | [ ] Pending | Phase 04, 10, 11 |

### Stage 4: Platform & Configuration (V0.4)

| Phase | Title | Status | Dependencies |
|-------|-------|--------|--------------|
| 13 | 多显示器支持 | [ ] Pending | Phase 09, 04 |
| 14 | 配置界面 | [ ] Pending | Phase 05, 08 |
| 15 | 跨平台适配 | [ ] Pending | Phase 09, 03 |

### Stage 5: Release Readiness (V1.0)

| Phase | Title | Status | Dependencies |
|-------|-------|--------|--------------|
| 16 | 安全与确认机制 | [ ] Pending | Phase 06, 08 |
| 17 | 隐私保护 | [ ] Pending | Phase 09, 16 |
| 18 | 动画状态机完善 | [ ] Pending | Phase 04, 12 |
| 19 | 资源优化与打包 | [ ] Pending | All prior |

## Notes
- Godot 前端使用 GDScript 2.0，Python 后端使用 async/await 异步模式
- PaddleOCR 仅在 Agent 无法通过常规 API 获取信息时触发（按需 OCR）
- 模型资产按阶段迭代：占位图 → SpriteSheet → Spine/Live2D → VRM 3D
- WebSocket 消息协议需版本化，为未来扩展留空间
