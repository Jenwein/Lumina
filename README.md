# Lumina — Interactive AI Desktop Pet Agent

Lumina brings your desktop to life. It combines LLM reasoning with a Godot-rendered desktop pet to create an interactive assistant that can see your screen, operate applications, and provide visual feedback through a charming companion.

## Architecture

```
┌─────────────────┐   WebSocket (JSON)   ┌──────────────────┐
│  Lumina Server   │◄───────────────────►│  Lumina Client    │
│  (Python/FastAPI)│                      │  (Godot 4.x)     │
│                  │                      │                   │
│  ├─ Agent Engine │                      │  ├─ Pet Renderer  │
│  ├─ LLM Client   │                      │  ├─ State Machine │
│  ├─ Tool System  │                      │  ├─ Dialogue UI   │
│  ├─ Vision/OCR   │                      │  └─ Settings UI   │
│  └─ Config       │                      │                   │
└─────────────────┘                      └──────────────────┘
```

## Project Structure

```
Lumina/
├── server/                        # Python 后端
│   ├── pyproject.toml             # uv 项目配置 & 依赖
│   ├── config.example.yaml        # 配置文件模板
│   ├── src/lumina/
│   │   ├── main.py                # FastAPI 入口
│   │   ├── agent/                 # ReAct Agent 引擎
│   │   ├── llm/                   # 多模型 LLM 集成
│   │   ├── tools/                 # 工具系统 (文件/输入/系统)
│   │   ├── vision/                # 屏幕截取 & OCR
│   │   ├── ws/                    # WebSocket 通信层
│   │   └── config/                # 配置管理
│   └── tests/                     # pytest 测试
├── client/                        # Godot 4.x 前端
│   ├── project.godot              # Godot 项目文件
│   ├── scenes/                    # 场景文件 (.tscn)
│   ├── scripts/                   # GDScript 脚本
│   │   ├── ws/                    # WebSocket 客户端
│   │   ├── pet/                   # 桌宠控制 & 动画
│   │   ├── ui/                    # 对话气泡 & 菜单
│   │   └── system/                # 电源管理等
│   ├── assets/                    # 素材资源
│   └── addons/                    # Godot 插件
├── docs/tasks/lumina/             # 任务分解文档 (task-architect)
│   ├── master_overview.md         # 总览 & 状态追踪
│   ├── changelog.md               # 变更日志
│   ├── api_registry/              # 接口注册表
│   └── stages/                    # 5 个 Stage, 19 个 Phase 文档
└── PRD.md                         # 产品需求文档
```

## Prerequisites

- **Python** >= 3.11
- **uv** (Python package manager): https://docs.astral.sh/uv/
- **Godot Engine** 4.x: https://godotengine.org/download

## Quick Start

### Python Backend

```bash
cd server
uv sync                              # 安装依赖
uv run uvicorn lumina.main:app --reload   # 启动开发服务器
```

Health check: http://127.0.0.1:8000/health

### Godot Frontend

1. Open Godot 4.x editor
2. Import project: select `client/project.godot`
3. Press F5 to run

## Development Workflow

This project uses **task-architect** for document-driven development:

```
docs/tasks/lumina/master_overview.md   # 查看整体进度
docs/tasks/lumina/stages/              # 查看各 Phase 详细设计
```

Each phase follows: **Validate → Decompose → Execute (TDD) → Teardown**

| Command | Description |
|---------|-------------|
| `Execute Lumina Phase X` | 执行指定 Phase |
| Read `master_overview.md` | 查看当前状态 |
| Read `changelog.md` | 查看变更历史 |

## Milestones

| Version | Milestone | Status |
|---------|-----------|--------|
| V0.1 | WebSocket 连通 + 桌宠移动 | In Progress |
| V0.2 | Agent 对话 + 文件操作工具 | Pending |
| V0.3 | 截图 + OCR + 视觉点击链路 | Pending |
| V0.4 | 跨平台 + 配置界面 | Pending |
| V1.0 | 正式发布 | Pending |

## License

TBD
