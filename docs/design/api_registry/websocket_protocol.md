# API Registry — WebSocket 通信协议

> 本文档记录 Python 后端与 Godot 前端之间所有 WebSocket 消息类型的接口定义。

## 消息信封格式

所有消息遵循统一信封：

```json
{
  "type": "<message_type>",
  "id": "<uuid4>",
  "timestamp": "<ISO 8601>",
  "payload": { }
}
```

## 消息类型一览

| Interface | File Path | Origin Phase (Link) | Usage Note |
|-----------|-----------|---------------------|------------|
| `MessageType` 枚举 | `server/lumina/ws/protocol.py` | [Phase 01](../phases/phase_01_infrastructure.md) | 所有消息类型的枚举定义 |
| `Message` 数据类 | `server/lumina/ws/protocol.py` | [Phase 01](../phases/phase_01_infrastructure.md) | `to_json()` / `from_json()` 序列化 |

## Client → Server 消息

| type | payload 结构 | Origin Phase | 说明 |
|------|-------------|-------------|------|
| `user_message` | `{"text": str}` | [Phase 01](../phases/phase_01_infrastructure.md) | 用户输入文本 |
| `user_action` | `{"action": "confirm"\|"cancel", "request_id": str}` | [Phase 01](../phases/phase_01_infrastructure.md) | 用户对确认框的响应 |
| `client_ready` | `{"version": str}` | [Phase 01](../phases/phase_01_infrastructure.md) | 客户端就绪通知 |
| `pet_event` | `{"event": str, ...}` | [Phase 05](../phases/phase_05_screen_vision.md) | 桌宠事件上报 (arrived, click_ready, animation_finished) |
| `config_get` | `{}` | [Phase 08](../phases/phase_08_platform_polish.md) | 请求当前配置 |
| `config_update` | `{"models": [...], "active_model": str}` | [Phase 08](../phases/phase_08_platform_polish.md) | 更新配置 |
| `config_test_model` | `{"model_name": str}` | [Phase 08](../phases/phase_08_platform_polish.md) | 测试模型连接 |
| `emergency_stop` | `{}` | [Phase 07](../phases/phase_07_security_privacy.md) | 紧急停止 |

## Server → Client 消息

| type | payload 结构 | Origin Phase | 说明 |
|------|-------------|-------------|------|
| `server_ready` | `{"version": str, "capabilities": [str], "monitors": [...]}` | [Phase 01](../phases/phase_01_infrastructure.md), [Phase 07](../phases/phase_07_security_privacy.md) | 服务端就绪/握手 |
| `pet_command` | `{"command": str, "data": {...}}` | [Phase 01](../phases/phase_01_infrastructure.md) | 控制桌宠 |
| `agent_status` | `{"status": str, "message": str}` | [Phase 01](../phases/phase_01_infrastructure.md) | Agent 状态变更 |
| `chat_response` | `{"text": str, "streaming": bool, "done": bool}` | [Phase 01](../phases/phase_01_infrastructure.md) | 对话回复 |
| `confirmation_request` | `{"description": str, "risk_level": str, "request_id": str}` | [Phase 01](../phases/phase_01_infrastructure.md), [Phase 07](../phases/phase_07_security_privacy.md) | 高危操作确认 |
| `config_data` | `{完整配置}` | [Phase 08](../phases/phase_08_platform_polish.md) | 返回当前配置 |
| `config_test_result` | `{"model_name": str, "success": bool, "message": str}` | [Phase 08](../phases/phase_08_platform_polish.md) | 测试结果 |

## 双向消息

| type | payload 结构 | Origin Phase | 说明 |
|------|-------------|-------------|------|
| `heartbeat` | `{}` | [Phase 01](../phases/phase_01_infrastructure.md) | 心跳保活 (30s) |
| `error` | `{"code": int, "message": str}` | [Phase 01](../phases/phase_01_infrastructure.md) | 错误通知 |

## pet_command 子命令

| command | data | Origin Phase |
|---------|------|-------------|
| `move_to` | `{"x": int, "y": int, "speed": float}` | [Phase 01](../phases/phase_01_infrastructure.md) |
| `set_state` | `{"state": str}` | [Phase 01](../phases/phase_01_infrastructure.md) |
| `show_bubble` | `{"text": str, "duration": float\|null}` | [Phase 01](../phases/phase_01_infrastructure.md) |
| `hide_bubble` | `{}` | [Phase 01](../phases/phase_01_infrastructure.md) |
