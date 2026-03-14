# Phase 01: 项目基础设施与 WebSocket 通信协议

## §1 Goal

搭建 Python 后端与 Godot 前端的项目骨架，定义并实现双端 WebSocket 通信协议，使两端能建立稳定连接并双向收发 JSON 消息。本阶段完成后，可通过命令行启动 Python 服务端，Godot 客户端自动连接并完成握手。

## §2 Dependencies

- **Prerequisite phases**: 无 (首个阶段)
- **Reference Materials**:
    - [ ] [PRD — 技术路线图与架构](../../../PRD.md) §3
    - [ ] [Godot WebSocketPeer 文档](../../godot/godot-docs/tutorials/networking/websocket.rst)
    - [ ] [Godot DisplayServer 文档](../../godot/godot-docs/classes/class_displayserver.rst)
- **Source files to read**:
    - [ ] 本阶段为初始阶段，无已有源码

## §3 Design & Constraints

### 项目目录结构

```
Lumina/
├── server/                     # Python 后端
│   ├── pyproject.toml          # 项目元数据与依赖
│   ├── lumina/
│   │   ├── __init__.py
│   │   ├── __main__.py         # 入口: python -m lumina
│   │   ├── config.py           # 配置管理 (端口、模型等)
│   │   ├── ws/
│   │   │   ├── __init__.py
│   │   │   ├── server.py       # WebSocket 服务端
│   │   │   └── protocol.py     # 消息协议定义
│   │   ├── agent/              # Phase 03 填充
│   │   ├── tools/              # Phase 04 填充
│   │   └── vision/             # Phase 05 填充
│   └── tests/
│       ├── __init__.py
│       └── test_ws.py
├── client/                     # Godot 前端
│   ├── project.godot
│   ├── scripts/
│   │   ├── main.gd             # 主场景脚本
│   │   ├── ws_client.gd        # WebSocket 客户端
│   │   └── pet/                # Phase 02 填充
│   ├── scenes/
│   │   └── main.tscn           # 主场景
│   └── assets/                 # 资源目录
│       ├── sprites/
│       └── fonts/
├── docs/
├── PRD.md
└── README.md
```

### WebSocket 协议设计

**传输层**:
- 协议: WebSocket (RFC 6455)
- 默认地址: `ws://localhost:8765`
- 端口可通过配置文件或命令行参数覆盖
- 帧格式: Text frames, UTF-8 编码 JSON

**消息信封 (Envelope)**:

所有消息遵循统一信封格式：

```json
{
  "type": "<message_type>",
  "id": "<uuid4>",
  "timestamp": "<ISO 8601>",
  "payload": { }
}
```

**消息类型定义**:

| 方向 | type | 用途 | payload 概要 |
|------|------|------|-------------|
| C→S | `user_message` | 用户输入文本 | `{"text": "..."}` |
| C→S | `user_action` | 用户对确认框的响应 | `{"action": "confirm"\|"cancel", "request_id": "..."}` |
| C→S | `client_ready` | 客户端就绪通知 | `{"version": "0.1.0"}` |
| S→C | `pet_command` | 控制桌宠行为 | `{"command": "...", "data": {...}}` |
| S→C | `agent_status` | Agent 状态变更 | `{"status": "...", "message": "..."}` |
| S→C | `chat_response` | 对话回复 (流式/完整) | `{"text": "...", "streaming": bool, "done": bool}` |
| S→C | `confirmation_request` | 高危操作确认请求 | `{"description": "...", "risk_level": "...", "request_id": "..."}` |
| S→C | `server_ready` | 服务端就绪/握手确认 | `{"version": "0.1.0", "capabilities": [...]}` |
| 双向 | `heartbeat` | 心跳保活 | `{}` |
| 双向 | `error` | 错误通知 | `{"code": int, "message": "..."}` |

**pet_command 子命令**:

| command | data | 说明 |
|---------|------|------|
| `move_to` | `{"x": int, "y": int, "speed": float}` | 移动到屏幕坐标 |
| `set_state` | `{"state": "idle"\|"thinking"\|"walking"\|"typing"\|"observing"\|"clicking"\|"celebrating"\|"failing"}` | 切换动画状态 |
| `show_bubble` | `{"text": "...", "duration": float\|null}` | 显示对话气泡 |
| `hide_bubble` | `{}` | 隐藏对话气泡 |

**连接生命周期**:

```
Python Server 启动
       │
       ▼
  监听 ws://localhost:8765
       │
       │◄──── Godot Client 连接
       │
       ▼
  收到 client_ready
       │
       ▼
  发送 server_ready (握手完成)
       │
       ▼
  进入正常消息循环
       │
  ┌────┴────┐
  │ 心跳检测 │ (每 30s 一次，超时 90s 断开)
  └─────────┘
```

### Architecture Principles

- **单连接模型**: 一个 Python 服务端同时只服务一个 Godot 客户端
- **无状态消息**: 每条消息自包含，不依赖之前消息的顺序（心跳除外）
- **优雅降级**: 连接断开后客户端自动尝试重连（指数退避，最大间隔 30s）
- **配置外置**: 端口号、心跳间隔等参数均可通过 `config.yaml` 或环境变量覆盖

### Out of scope

- Agent 逻辑 / LLM 调用 (Phase 03)
- 桌宠动画与视觉渲染 (Phase 02)
- 任何工具调用 (Phase 04+)

## §4 Interface Contract

### Python 端

```python
# server/lumina/ws/protocol.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Any
import uuid
from datetime import datetime, timezone


class MessageType(str, Enum):
    USER_MESSAGE = "user_message"
    USER_ACTION = "user_action"
    CLIENT_READY = "client_ready"
    PET_COMMAND = "pet_command"
    AGENT_STATUS = "agent_status"
    CHAT_RESPONSE = "chat_response"
    CONFIRMATION_REQUEST = "confirmation_request"
    SERVER_READY = "server_ready"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


@dataclass
class Message:
    type: MessageType
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self) -> str: ...

    @classmethod
    def from_json(cls, raw: str) -> "Message": ...


# server/lumina/ws/server.py
import asyncio
from websockets.asyncio.server import serve

class JsonWebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def send(self, message: Message) -> None: ...
    def on_message(self, handler: Callable[[Message], Awaitable[None]]) -> None: ...


# server/lumina/config.py
from dataclasses import dataclass

@dataclass
class LuminaConfig:
    ws_host: str = "localhost"
    ws_port: int = 8765
    heartbeat_interval: float = 30.0
    heartbeat_timeout: float = 90.0

    @classmethod
    def load(cls, path: str = "config.yaml") -> "LuminaConfig": ...
```

### Godot 端 (GDScript)

```gdscript
# client/scripts/ws_client.gd
class_name LuminaWSClient
extends Node

signal connected
signal disconnected
signal message_received(msg: Dictionary)

var server_url: String = "ws://localhost:8765"

func connect_to_server() -> Error: ...
func send_message(type: String, payload: Dictionary = {}) -> void: ...
func _send_client_ready() -> void: ...
func _start_heartbeat() -> void: ...
func _handle_reconnect() -> void: ...
```

## §5 Implementation Steps

1. **初始化 Python 项目**: 在 `server/` 下创建 `pyproject.toml`，声明 `websockets`, `pyyaml`, `pydantic` 依赖。创建 `lumina/` 包结构。
2. **实现消息协议** (`server/lumina/ws/protocol.py`): 实现 `MessageType` 枚举和 `Message` 数据类，包含 JSON 序列化/反序列化。
3. **实现 WebSocket 服务端** (`server/lumina/ws/server.py`): 基于 `websockets` 库实现 `LuminaWSServer`，支持连接管理、消息路由、心跳检测。
4. **实现配置管理** (`server/lumina/config.py`): 支持从 YAML 文件和环境变量加载配置。
5. **创建 Python 入口** (`server/lumina/__main__.py`): 实现 `python -m lumina` 启动命令。
6. **初始化 Godot 项目**: 在 `client/` 下创建 Godot 4.6 项目，配置 `project.godot`。
7. **实现 Godot WebSocket 客户端** (`client/scripts/ws_client.gd`): 使用 `WebSocketPeer` 实现连接、消息收发、心跳和自动重连。
8. **创建主场景** (`client/scenes/main.tscn`): 最小化场景，挂载 `ws_client.gd`，启动时自动连接。
9. **编写集成测试** (`server/tests/test_ws.py`): 测试连接握手、消息收发、心跳超时。

## §6 Acceptance Criteria

- [ ] `python -m lumina` 启动后在终端显示 "Listening on ws://localhost:8765"
- [ ] Godot 客户端启动后自动连接，双端完成 `client_ready` / `server_ready` 握手
- [ ] Python 端发送 `pet_command` 消息，Godot 端正确接收并解析（打印到控制台）
- [ ] Godot 端发送 `user_message`，Python 端正确接收并回显
- [ ] 断开连接后，Godot 客户端在 5s 内自动重连
- [ ] 心跳超时 90s 后服务端主动断开连接
- [ ] `pytest server/tests/test_ws.py` 全部通过

## §7 State Teardown Checklist

- [ ] **Phase Document Updated** (if design changed during implementation)
- [ ] `changelog.md` updated
- [ ] `api_registry/websocket_protocol.md` updated
- [ ] `master_overview.md` Phase 01 status set to `[x] Done`
