# Phase 04: 运动与指令系统

## §1 Goal
实现桌宠根据 WebSocket 指令在屏幕上平滑移动的能力，建立基础动画状态机（Idle/Moving）。

## §2 Dependencies
- **Prerequisite phases**: Phase 02, Phase 03
- **Source files to read**: `client/scripts/ws/ws_client.gd`, `client/scripts/pet/pet_window.gd`

## §3 Design & Constraints
- **Architecture principles**:
  - 使用 Tween 实现平滑插值移动到目标坐标
  - 基础状态机：`IDLE`（默认）、`MOVING`（移动中）
  - 通过 WebSocket 接收来自 Python 的命令：`move_to`、`set_position`、`get_position`
  - 移动速度可配置，使用缓动曲线实现自然手感
- **Boundary conditions**:
  - 目标坐标不得超出屏幕边界，需做边界裁剪
  - 新的 `move_to` 命令可中断当前移动
  - 到达目标后自动回到 IDLE 状态并发送事件通知
- **Out of scope**: 高级动画（思考、点击反馈）、跨显示器移动、路径规划

## §4 Interface Contract

### GDScript

```gdscript
# client/scripts/pet/pet_controller.gd
class_name PetController extends Node

enum State { IDLE, MOVING }

var current_state: State = State.IDLE

func move_to(target: Vector2, speed: float = 200.0) -> void: ...
func stop() -> void: ...

signal arrived_at_target()
signal state_changed(new_state: State)
```

### Python 命令协议（通过 WebSocket 发送）

```python
# 服务端发送的命令
{"action": "move_to", "payload": {"x": 500, "y": 300, "speed": 200}}
{"action": "set_position", "payload": {"x": 100, "y": 100}}
{"action": "get_position", "payload": {}}

# 客户端返回的响应
{"action": "position_report", "payload": {"x": 100, "y": 100, "state": "idle"}}
{"action": "arrived", "payload": {"x": 500, "y": 300}}
```

## §5 Implementation Steps
1. 创建 `client/scripts/pet/pet_state_machine.gd` — 基于枚举的状态机，管理 IDLE/MOVING 状态转换
2. 创建 `client/scripts/pet/pet_controller.gd` — 使用 Tween 实现移动 + 状态转换逻辑
3. 创建 `client/scripts/ws/command_handler.gd` — 解析 WebSocket 命令并分发到 PetController
4. 更新 `client/scenes/pet/pet.tscn` — 添加 PetController 节点到场景树
5. 在 `server/src/lumina/ws/` 中添加移动命令发送工具（用于测试）
6. 创建集成测试：Python 发送 `move_to` → 桌宠移动 → 到达事件回传

## §6 Acceptance Criteria
- [ ] Python 发送 `move_to` 命令后，桌宠平滑移动到目标坐标
- [ ] 桌宠状态正确转换：IDLE → MOVING → IDLE（到达目标后）
- [ ] 到达目标后通过 WebSocket 发送 `arrived` 事件回 Python
- [ ] `get_position` 命令返回当前桌宠坐标和状态
- [ ] 新的 `move_to` 命令可中断当前移动，桌宠转向新目标
- [ ] 移动不超出屏幕边界

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
