# API Registry — Godot UI 层

> 本文档记录 Godot 客户端的核心接口，包括桌宠控制、状态机、窗口管理和 UI 组件。

## 核心组件

| Interface | File Path | Origin Phase (Link) | Usage Note |
|-----------|-----------|---------------------|------------|
| `LuminaWSClient` | `client/scripts/ws_client.gd` | [Phase 01](../phases/phase_01_infrastructure.md) | WebSocket 客户端。信号: connected, disconnected, message_received |
| `PetController` | `client/scripts/pet/pet_controller.gd` | [Phase 02](../phases/phase_02_godot_pet.md) | 桌宠主控制器。`move_to()`, `set_pet_state()` |
| `PetStateMachine` | `client/scripts/pet/pet_state_machine.gd` | [Phase 02](../phases/phase_02_godot_pet.md) | 通用状态机。`transition_to(state_name)` |
| `PetState` | `client/scripts/pet/pet_state.gd` | [Phase 02](../phases/phase_02_godot_pet.md) | 状态基类。子类实现 enter/exit/update/physics_update |
| `WindowManager` | `client/scripts/window_manager.gd` | [Phase 02](../phases/phase_02_godot_pet.md) | 透明置顶窗口管理 + 鼠标穿透区域更新 |

## 状态枚举

| 状态名 | Origin Phase | 触发条件 |
|--------|-------------|---------|
| `idle` | [Phase 02](../phases/phase_02_godot_pet.md) | 默认待机，到达目标后自动切换 |
| `walking` | [Phase 02](../phases/phase_02_godot_pet.md) | 收到 `move_to` 指令 |
| `thinking` | [Phase 02](../phases/phase_02_godot_pet.md) | 收到 `set_state("thinking")` |
| `typing` | [Phase 02](../phases/phase_02_godot_pet.md) | 收到 `set_state("typing")` |
| `observing` | [Phase 05](../phases/phase_05_screen_vision.md) | 屏幕视觉分析中 |
| `clicking` | [Phase 05](../phases/phase_05_screen_vision.md) | 到达目标后播放点击动画 |
| `celebrating` | [Phase 05](../phases/phase_05_screen_vision.md) | 任务成功 |
| `failing` | [Phase 05](../phases/phase_05_screen_vision.md) | 任务失败 |

## 信号

| 信号 | 所在类 | Origin Phase | 说明 |
|------|--------|-------------|------|
| `connected` | `LuminaWSClient` | [Phase 01](../phases/phase_01_infrastructure.md) | WebSocket 连接建立 |
| `disconnected` | `LuminaWSClient` | [Phase 01](../phases/phase_01_infrastructure.md) | WebSocket 连接断开 |
| `message_received(msg)` | `LuminaWSClient` | [Phase 01](../phases/phase_01_infrastructure.md) | 收到消息 (Dictionary) |
| `arrived_at_target` | `PetController` | [Phase 02](../phases/phase_02_godot_pet.md) | 桌宠到达目标位置 |
| `state_changed(old, new)` | `PetController` | [Phase 02](../phases/phase_02_godot_pet.md) | 状态切换 |
| `click_ready(position)` | `PetController` | [Phase 05](../phases/phase_05_screen_vision.md) | 点击动画到达击中帧 |
| `action_completed` | `PetController` | [Phase 05](../phases/phase_05_screen_vision.md) | 整个动作序列完成 |
| `closed` | `SpeechBubble` | [Phase 07](../phases/phase_07_security_privacy.md) | 气泡关闭 |
| `emergency_stop_pressed` | `PetContextMenu` | [Phase 07](../phases/phase_07_security_privacy.md) | 紧急停止 |
| `config_changed(config)` | `SettingsPanel` | [Phase 08](../phases/phase_08_platform_polish.md) | 配置变更 |

## UI 组件

| Interface | File Path | Origin Phase (Link) | Usage Note |
|-----------|-----------|---------------------|------------|
| `SpeechBubble` | `client/scripts/ui/speech_bubble.gd` | [Phase 07](../phases/phase_07_security_privacy.md) | `show_message()` 普通气泡; `show_confirmation()` 确认气泡 |
| `PetContextMenu` | `client/scripts/ui/context_menu.gd` | [Phase 07](../phases/phase_07_security_privacy.md) | 右键菜单: 设置/模型切换/日志/紧急停止 |
| `SettingsPanel` | `client/scripts/ui/settings_panel.gd` | [Phase 08](../phases/phase_08_platform_polish.md) | 多模型配置面板 |
| `PerformanceManager` | `client/scripts/performance_manager.gd` | [Phase 08](../phases/phase_08_platform_polish.md) | 低功耗模式: 闲置降帧 60fps → 10fps |

## 场景树结构

```
Main (Node2D)
├── WSClient (Node)                 # LuminaWSClient
├── WindowManager (Node)            # WindowManager
├── PerformanceManager (Node)       # PerformanceManager (Phase 08)
├── Pet (CharacterBody2D)           # PetController
│   ├── Sprite (AnimatedSprite2D)
│   ├── ClickArea (Area2D)
│   │   └── CollisionShape2D
│   └── StateMachine (Node)         # PetStateMachine
│       ├── IdleState (Node)
│       ├── WalkingState (Node)
│       ├── ThinkingState (Node)
│       ├── TypingState (Node)
│       ├── ObservingState (Node)   # Phase 05
│       └── ClickingState (Node)    # Phase 05
├── BubbleUI (Control)              # SpeechBubble (Phase 07)
├── ContextMenu (PopupMenu)         # PetContextMenu (Phase 07)
└── SettingsPanel (Control)         # SettingsPanel (Phase 08)
```
