# Phase 08: 对话气泡 UI

## §1 Goal
在 Godot 中实现对话气泡系统（自动尺寸、流式文字）和右键菜单（设置、模型切换、日志、紧急停止）。

## §2 Dependencies
- **Prerequisite phases**: Phase 04, Phase 06
- **Source files to read**: `client/scripts/ws/ws_client.gd`, `client/scripts/pet/pet_controller.gd`

## §3 Design & Constraints
- **Architecture principles**:
  - 对话气泡：`RichTextLabel` 嵌入 `NinePatchRect`/`Panel`，锚定在桌宠精灵上方
  - 自动尺寸：根据文本内容动态调整，最大宽度封顶
  - 流式文字：逐字符显示（打字机效果），支持从 WebSocket 接收流式文本
  - 淡入/淡出动画
  - 右键菜单：使用 `PopupMenu` 节点
  - 菜单项：设置、切换模型、查看日志、紧急停止
  - 气泡显示时禁用鼠标穿透，确保用户可以交互
- **Boundary conditions**:
  - 气泡不得超出屏幕边界，需自动调整位置
  - 流式文本累积不超过最大字符数限制（默认 2000 字符）
  - 气泡可设置自动消失时间（duration 参数，0 表示手动关闭）
  - 右键菜单仅在桌宠区域触发
- **Out of scope**: 设置面板 UI（Phase 14）、实际模型切换逻辑、日志查看器实现

## §4 Interface Contract

### 对话气泡

```gdscript
# client/scripts/ui/dialogue_bubble.gd
class_name DialogueBubble extends Control

func show_message(text: String, duration: float = 0.0) -> void: ...
func show_streaming() -> void: ...
func append_text(text: String) -> void: ...
func finish_streaming() -> void: ...
func hide_bubble() -> void: ...

signal bubble_shown()
signal bubble_hidden()
```

### 右键菜单

```gdscript
# client/scripts/ui/context_menu.gd
class_name PetContextMenu extends PopupMenu

signal action_selected(action: String)
# Actions: "settings", "switch_model", "view_logs", "emergency_stop"
```

### WebSocket → UI 映射

```gdscript
# client/scripts/ws/ui_command_handler.gd
class_name UICommandHandler extends Node

func handle_message(msg: Dictionary) -> void: ...
# Maps WebSocket events to UI actions:
#   "show_bubble" → DialogueBubble.show_message()
#   "stream_start" → DialogueBubble.show_streaming()
#   "stream_chunk" → DialogueBubble.append_text()
#   "stream_end" → DialogueBubble.finish_streaming()
```

## §5 Implementation Steps
1. 创建 `client/scenes/ui/dialogue_bubble.tscn` — 气泡场景：NinePatchRect + RichTextLabel + AnimationPlayer
2. 创建 `client/scripts/ui/dialogue_bubble.gd` — 文字显示、流式文本、自动尺寸调整、淡入淡出
3. 创建 `client/scenes/ui/context_menu.tscn` — 右键弹出菜单场景
4. 创建 `client/scripts/ui/context_menu.gd` — 菜单动作和信号处理
5. 更新 `client/scenes/main.tscn` — 将气泡和菜单集成到场景树
6. 创建 `client/scripts/ws/ui_command_handler.gd` — 将 WebSocket 事件映射到 UI 操作（显示气泡、流式文本）
7. 实现鼠标穿透切换：气泡或菜单激活时禁用穿透，隐藏后恢复

## §6 Acceptance Criteria
- [ ] 对话气泡出现在桌宠上方，显示正确文本
- [ ] 流式文字逐字符显示（打字机效果）
- [ ] 气泡根据文本内容自动调整尺寸，不超出屏幕边界
- [ ] 右键点击桌宠弹出菜单，包含所有菜单项（设置、切换模型、查看日志、紧急停止）
- [ ] 菜单动作触发正确的信号
- [ ] 气泡或菜单显示时鼠标穿透被禁用，隐藏后恢复
- [ ] 气泡淡入/淡出动画流畅
- [ ] WebSocket 流式消息正确映射到气泡的流式文本显示

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
