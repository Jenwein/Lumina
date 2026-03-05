# Phase 02: WebSocket 通信协议

## §1 Goal
设计并实现 Python ↔ Godot 的 WebSocket 双向通信层，定义 JSON 消息协议。

## §2 Dependencies
- **Prerequisite phases**: Phase 01
- **Source files to read**: `server/src/lumina/main.py`, `server/src/lumina/ws/`

## §3 Design & Constraints
- **Architecture principles**:
  - 四种消息类型：`command`（服务端→客户端）、`response`（客户端→服务端）、`event`（双向）、`heartbeat`
  - 统一消息格式：`{ "type": str, "id": str, "action": str, "payload": dict, "timestamp": float }`
  - Python 端：FastAPI WebSocket 端点挂载于 `/ws`
  - Godot 端：`WebSocketPeer` 客户端，支持自动重连
  - 心跳间隔 5 秒，用于检测断连
  - 所有消息通过 Pydantic 模型校验
- **Boundary conditions**:
  - 单连接模式（一个 Godot 客户端对应一个服务端）
  - 消息 payload 为任意 JSON 可序列化字典
  - 重连策略：指数退避，最大间隔 30 秒
- **Out of scope**: 实际命令处理器、桌宠运动逻辑

## §4 Interface Contract

### Python 端

```python
# server/src/lumina/ws/models.py
from pydantic import BaseModel, Field
from typing import Literal
from uuid import uuid4
import time

class WSMessage(BaseModel):
    type: Literal["command", "response", "event", "heartbeat"]
    id: str = Field(default_factory=lambda: uuid4().hex)
    action: str
    payload: dict = {}
    timestamp: float = Field(default_factory=time.time)
```

```python
# server/src/lumina/ws/server.py
from fastapi import WebSocket

class ConnectionManager:
    async def connect(self, websocket: WebSocket) -> None: ...
    async def disconnect(self, websocket: WebSocket) -> None: ...
    async def send(self, websocket: WebSocket, message: WSMessage) -> None: ...
    async def broadcast(self, message: WSMessage) -> None: ...
```

### Godot 端

```gdscript
# client/scripts/ws/ws_client.gd
class_name WSClient extends Node

signal connected()
signal disconnected()
signal message_received(msg: Dictionary)

func connect_to_server(url: String) -> Error: ...
func send_message(msg: Dictionary) -> Error: ...
func disconnect_from_server() -> void: ...
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/ws/models.py` — 定义 `WSMessage` Pydantic 模型
2. 创建 `server/src/lumina/ws/server.py` — 实现 `ConnectionManager` 类（连接管理、收发消息、广播）
3. 在 `server/src/lumina/main.py` 中添加 WebSocket 端点 `/ws`，使用 `ConnectionManager`
4. 创建 `server/tests/test_ws.py` — 测试连接建立、消息收发、心跳机制
5. 创建 `client/scripts/ws/ws_client.gd` — WebSocket 客户端，含自动重连和指数退避
6. 编写消息协议文档 `docs/tasks/lumina/stages/stage_01_foundation/PROTOCOL.md`

## §6 Acceptance Criteria
- [ ] Python WebSocket 服务端启动后可在可配置端口上接受连接
- [ ] 可从 Python 端发送 JSON 消息，模拟客户端正确接收
- [ ] 心跳机制正常工作：5 秒间隔发送，超时检测断连
- [ ] 消息格式校验：不合法消息被拒绝并返回错误
- [ ] 所有测试通过：`uv run pytest server/tests/test_ws.py`
- [ ] Godot `WSClient` 可连接 Python 服务端并完成消息交换
- [ ] 断连后自动重连（指数退避策略）

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
