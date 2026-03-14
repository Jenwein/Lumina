# Phase 02: Godot 桌宠基础

## §1 Goal

在 Godot 4.6 中实现透明无边框置顶窗口，渲染一个可移动的 2D 桌宠角色，通过状态机控制动画切换，并接收 Phase 01 定义的 WebSocket `pet_command` 指令来驱动移动和状态变更。

## §2 Dependencies

- **Prerequisite phases**: Phase 01 (`[x] Done`)
- **Reference Materials**:
    - [ ] [PRD — 桌宠表现层](../../../PRD.md) §2.3
    - [ ] [Godot DisplayServer 类参考](../../godot/godot-docs/classes/class_displayserver.rst)
    - [ ] [Godot AnimatedSprite2D 类参考](../../godot/godot-docs/classes/class_animatedsprite2d.rst)
    - [ ] [Godot AnimationPlayer 类参考](../../godot/godot-docs/classes/class_animationplayer.rst)
    - [ ] [Godot WebSocketPeer 类参考](../../godot/godot-docs/classes/class_websocketpeer.rst)
    - [ ] [Godot Window 类参考](../../godot/godot-docs/classes/class_window.rst)
    - [ ] [Godot InputEventMouse 文档](../../godot/godot-docs/classes/class_inputeventmouse.rst)
- **Source files to read**:
    - [ ] `client/scripts/ws_client.gd` (Phase 01 产出)
    - [ ] `client/scenes/main.tscn` (Phase 01 产出)

## §3 Design & Constraints

### 窗口配置

Godot `project.godot` 需要配置以下关键属性：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `display/window/size/transparent` | `true` | 启用透明背景 |
| `display/window/per_pixel_transparency/allowed` | `true` | 允许像素级透明 |
| `display/window/size/borderless` | `true` | 无边框 |
| `display/window/size/always_on_top` | `true` | 窗口置顶 |
| `rendering/viewport/transparent_background` | `true` | 渲染背景透明 |

### 鼠标穿透机制

桌宠窗口需要在大部分区域允许鼠标事件穿透到下层窗口，仅在桌宠角色本体区域拦截点击事件：

- 使用 `DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_MOUSE_PASSTHROUGH, true)` 启用全局穿透
- 通过 `DisplayServer.window_set_mouse_passthrough(polygon)` 设置穿透例外区域（桌宠可交互区域）
- 当显示对话气泡或右键菜单时，动态扩大非穿透区域

### 场景树结构

```
Main (Node2D)
├── WSClient (Node)              # Phase 01 的 WebSocket 客户端
├── Pet (CharacterBody2D)        # 桌宠主节点
│   ├── Sprite (AnimatedSprite2D) # 动画精灵
│   ├── ClickArea (Area2D)       # 可交互区域（用于计算穿透多边形）
│   │   └── CollisionShape2D
│   └── StateMachine (Node)      # 状态机控制器
│       ├── IdleState (Node)
│       ├── WalkingState (Node)
│       ├── ThinkingState (Node)
│       └── TypingState (Node)
├── BubbleUI (Control)           # 对话气泡 (Phase 07 完善)
└── ContextMenu (PopupMenu)      # 右键菜单 (Phase 07 完善)
```

### 状态机设计

```
                ┌──────────┐
        ┌──────►│   Idle   │◄──────┐
        │       └────┬─────┘       │
        │            │             │
   到达目标      move_to指令    动作完成
        │            │             │
        │       ┌────▼─────┐       │
        │       │ Walking  │       │
        │       └──────────┘       │
        │                          │
   ┌────┴─────┐            ┌───────┴──────┐
   │ Thinking │            │   Clicking   │
   └──────────┘            └──────────────┘
        ▲                          ▲
        │                          │
   set_state               set_state
   "thinking"              "clicking"
```

**状态枚举 (本阶段实现)**:
- `IDLE`: 待机播放呼吸/微动动画
- `WALKING`: 向目标位置平滑移动，播放行走动画
- `THINKING`: 播放思考动画（如头顶冒泡）
- `TYPING`: 播放打字动画

**状态枚举 (后续阶段追加)**:
- `OBSERVING`: Phase 05 — 视觉分析时的观察动画
- `CLICKING`: Phase 05 — 到达目标后的点击动作
- `CELEBRATING`: Phase 05 — 任务成功动画
- `FAILING`: Phase 05 — 任务失败动画

### 移动系统

- 收到 `move_to` 指令后，桌宠从当前位置向目标位置平滑移动
- 使用 `move_toward()` 或 Tween 实现平滑插值
- 移动速度由指令的 `speed` 参数控制（单位: px/s），默认 200
- 根据移动方向自动翻转 Sprite (`flip_h`)
- 到达目标后自动切换回 `IDLE` 状态

### 临时美术资源

本阶段使用占位符美术资源：
- 一个简单的 32x32 或 64x64 像素角色 SpriteSheet
- 包含 idle (2帧)、walk (4帧)、think (2帧) 基础动画
- 可使用纯色方块 + 简单表情作为最小可行原型

### Out of scope

- 对话气泡的完整 UI (Phase 07)
- 右键菜单功能 (Phase 07)
- 视觉分析相关状态 (Phase 05)
- 跨屏移动逻辑 (Phase 07)
- 高级动画资产 (Phase 08)

## §4 Interface Contract

### Godot 端

```gdscript
# client/scripts/pet/pet_controller.gd
class_name PetController
extends CharacterBody2D

signal arrived_at_target
signal state_changed(old_state: StringName, new_state: StringName)

func move_to(target: Vector2, speed: float = 200.0) -> void:
    ## 开始向目标位置移动，自动切换到 WALKING 状态
    pass

func set_pet_state(state: StringName) -> void:
    ## 切换桌宠状态，触发对应动画
    pass

func get_pet_state() -> StringName:
    ## 获取当前状态
    pass


# client/scripts/pet/pet_state_machine.gd
class_name PetStateMachine
extends Node

var current_state: PetState

func transition_to(state_name: StringName) -> void:
    ## 切换到指定状态
    pass


# client/scripts/pet/pet_state.gd
class_name PetState
extends Node

func enter() -> void: ...
func exit() -> void: ...
func update(delta: float) -> void: ...
func physics_update(delta: float) -> void: ...


# client/scripts/pet/states/idle_state.gd
class_name IdleState
extends PetState

# client/scripts/pet/states/walking_state.gd
class_name WalkingState
extends PetState

var target_position: Vector2
var move_speed: float


# client/scripts/main.gd (更新 — 桥接 WS 消息与 Pet 控制)
extends Node2D

@onready var ws_client: LuminaWSClient = $WSClient
@onready var pet: PetController = $Pet

func _on_ws_message_received(msg: Dictionary) -> void:
    ## 路由 WebSocket 消息到对应处理器
    match msg.type:
        "pet_command":
            _handle_pet_command(msg.payload)

func _handle_pet_command(payload: Dictionary) -> void:
    match payload.command:
        "move_to":
            pet.move_to(
                Vector2(payload.data.x, payload.data.y),
                payload.data.get("speed", 200.0)
            )
        "set_state":
            pet.set_pet_state(payload.data.state)
```

### 窗口管理

```gdscript
# client/scripts/window_manager.gd
class_name WindowManager
extends Node

func setup_transparent_overlay() -> void:
    ## 配置窗口为透明置顶覆盖层
    pass

func update_passthrough_region(pet_rect: Rect2, extra_rects: Array[Rect2] = []) -> void:
    ## 更新鼠标穿透区域（排除桌宠和 UI 区域）
    pass

func get_screen_size() -> Vector2i:
    ## 获取当前屏幕分辨率
    pass
```

## §5 Implementation Steps

1. **配置 Godot 项目**: 修改 `project.godot`，启用透明背景、无边框、置顶等窗口属性。
2. **实现窗口管理** (`client/scripts/window_manager.gd`): 初始化透明覆盖窗口，实现鼠标穿透区域的动态更新。
3. **创建占位符美术资源**: 制作最小 SpriteSheet (idle/walk/think)，放入 `client/assets/sprites/`。
4. **实现状态机框架** (`client/scripts/pet/pet_state_machine.gd`, `pet_state.gd`): 通用状态机，支持状态注册、转换和生命周期回调。
5. **实现具体状态**: `idle_state.gd`, `walking_state.gd`, `thinking_state.gd`, `typing_state.gd`。
6. **实现桌宠控制器** (`client/scripts/pet/pet_controller.gd`): 集成状态机、Sprite 动画和移动逻辑。
7. **搭建场景树** (`client/scenes/main.tscn`): 按设计组装场景节点。
8. **桥接 WebSocket 与 Pet**: 更新 `main.gd`，将收到的 `pet_command` 消息路由到 `PetController`。
9. **端到端测试**: Python 端发送 `move_to` 和 `set_state` 指令，验证桌宠响应。

## §6 Acceptance Criteria

- [x] Godot 窗口启动后背景完全透明，仅显示桌宠角色
- [x] 窗口始终置顶，桌宠以外区域的鼠标事件穿透到下层窗口
- [x] 右键桌宠角色可触发事件（本阶段打印日志即可）
- [x] 收到 `move_to` 指令后桌宠平滑移动到目标位置，到达后回到 idle
- [x] 收到 `set_state` 指令后桌宠切换到对应动画
- [x] 状态切换时发出 `state_changed` 信号
- [x] 桌宠朝移动方向自动翻转

## §7 State Teardown Checklist

- [x] **Phase Document Updated** (if design changed during implementation)
- [x] `changelog.md` updated
- [x] `api_registry/godot_ui.md` updated
- [x] `master_overview.md` Phase 02 status set to `[x] Done`
