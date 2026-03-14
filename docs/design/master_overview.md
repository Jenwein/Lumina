# Task: Lumina — 桌面 AI Agent 桌宠系统

## Meta
- **Created**: 2026-03-14
- **Last Updated**: 2026-03-14
- **Status**: In Progress
- **Complexity**: High

## Objective

将大语言模型的推理能力与 Godot 引擎渲染的桌面宠物相结合，构建一个具备自主操作能力（ReAct 循环）、屏幕视觉感知和情感化视觉反馈的交互式桌面 AI Agent。系统采用 Python 后端（Logic Server）+ Godot 前端（Display Client）的 C/S 架构，通过本地 WebSocket 通信。

## References & Knowledge Base

- **PRD**: [产品需求文档](../../PRD.md)
- **Godot 文档**: [Godot 官方文档仓库](../godot/godot-docs/) — Sphinx RST 格式，含 tutorials/、classes/ 等
- **Godot 引擎**: `C:\dev\Godot\Godot_v4.6.1-stable_win64_console.exe` (v4.6.1 stable, Windows 64-bit console build)
- **测试 API Key**: [GLM-4-Flash API Key](../../GLM_APIKEY) — 用于开发阶段的 LLM 调用测试
  - API Base URL: `https://open.bigmodel.cn/api/paas/v4/` (兼容 OpenAI 格式)
  - Model ID: `glm-4-flash`

## Constraints & Architecture Decisions

- **C/S 架构**: Python 后端为服务端，Godot 前端为客户端，职责严格分离。Agent 逻辑、工具调用、LLM 通信全部在 Python 端；Godot 端仅负责渲染、动画和用户输入采集。
- **通信协议**: 本地 WebSocket，端口可配置（默认 `ws://localhost:8765`），JSON 序列化。
- **多模型兼容**: 统一使用 OpenAI 兼容 API 格式，支持 GPT-4, Claude, DeepSeek, GLM, Ollama 等。
- **安全优先**: 高危操作必须经用户物理确认；支持应用黑名单和隐私遮罩。
- **跨平台目标**: Windows 原生 → macOS → Linux (X11 + Wayland)，但初期以 Windows 为主。
- **渐进式模型资产**: 阶段一 2D 序列帧 → 阶段二 Spine/Live2D → 阶段三 VRM 3D。

## Phase Map

### Stage 1: 基础通信 (V0.1)

| Phase | Title | Status | File Path | Dependencies |
|-------|-------|--------|-----------|--------------|
| 01 | 项目基础设施与 WebSocket 通信协议 | [ ] Pending | `./phases/phase_01_infrastructure.md` | — |
| 02 | Godot 桌宠基础 | [ ] Pending | `./phases/phase_02_godot_pet.md` | Phase 01 |

### Stage 2: 核心智能 (V0.2)

| Phase | Title | Status | File Path | Dependencies |
|-------|-------|--------|-----------|--------------|
| 03 | Agent 决策引擎 | [ ] Pending | `./phases/phase_03_agent_engine.md` | Phase 01 |
| 04 | 工具系统 | [ ] Pending | `./phases/phase_04_tool_system.md` | Phase 03 |

### Stage 3: 视觉智能 (V0.3)

| Phase | Title | Status | File Path | Dependencies |
|-------|-------|--------|-----------|--------------|
| 05 | 屏幕视觉与交互链路 | [ ] Pending | `./phases/phase_05_screen_vision.md` | Phase 02, Phase 04 |

### Stage 4: 扩展能力 (V0.4)

| Phase | Title | Status | File Path | Dependencies |
|-------|-------|--------|-----------|--------------|
| 06 | Web 自动化 | [ ] Pending | `./phases/phase_06_web_automation.md` | Phase 04 |
| 07 | 安全、隐私与多显示器 | [ ] Pending | `./phases/phase_07_security_privacy.md` | Phase 05 |

### Stage 5: 发布 (V1.0)

| Phase | Title | Status | File Path | Dependencies |
|-------|-------|--------|-----------|--------------|
| 08 | 跨平台适配、UI 打磨与发布 | [ ] Pending | `./phases/phase_08_platform_polish.md` | Phase 07 |

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Godot Client (Display)              │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ PetSprite │  │ StateMgr │  │ UI (Bubble/Menu) │  │
│  └─────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│        └──────────────┼─────────────────┘            │
│                       │                              │
│              ┌────────▼────────┐                     │
│              │ WebSocketClient │                     │
│              └────────┬────────┘                     │
└───────────────────────┼─────────────────────────────┘
                        │ ws://localhost:8765 (JSON)
┌───────────────────────┼─────────────────────────────┐
│              ┌────────▼────────┐                     │
│              │ WebSocketServer │                     │
│              └────────┬────────┘                     │
│                       │                              │
│  ┌────────────────────▼─────────────────────────┐    │
│  │            Agent Core (ReAct Loop)           │    │
│  │  Thought → Action → Observation → Thought…  │    │
│  └──────┬──────────────┬───────────────┬────────┘    │
│         │              │               │             │
│  ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────────┐  │
│  │ LLM Client  │ │ToolSystem │ │ Screen Vision   │  │
│  │ (OpenAI fmt)│ │(Registry) │ │ (OCR/Detection) │  │
│  └─────────────┘ └───────────┘ └─────────────────┘  │
│                  Python Server (Logic)               │
└─────────────────────────────────────────────────────┘
```

## Notes

- 初期开发环境为 Windows，Godot 4.6.1 console build。
- GLM-4-Flash 作为开发测试用模型，正式使用时用户可自由切换。
- Godot 端使用 GDScript 开发，Python 端使用 asyncio 异步架构。
- 所有跨进程通信均通过 WebSocket，不使用共享内存或管道。
