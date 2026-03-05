# Phase 03: Godot 桌宠窗口

## §1 Goal
创建透明背景、全屏置顶、支持鼠标穿透动态切换的 Godot 窗口，渲染占位角色精灵。

## §2 Dependencies
- **Prerequisite phases**: Phase 01
- **Source files to read**: `client/project.godot`, `client/scenes/`, `client/scripts/`

## §3 Design & Constraints
- **Architecture principles**:
  - 窗口设置：透明背景（逐像素 Alpha）、始终置顶、无边框、覆盖整个主显示器
  - 鼠标穿透：默认启用（点击穿透到下层窗口），当鼠标悬停在桌宠或 UI 元素上时自动禁用
  - 占位精灵：使用简单的几何形状（圆形或简易角色轮廓）作为临时占位图
  - 窗口尺寸等于主显示器分辨率
- **Boundary conditions**:
  - 仅支持主显示器，不处理多显示器场景
  - 透明区域必须实现真正的点击穿透（非视觉透明）
  - 桌宠精灵区域必须能接收鼠标事件
- **Out of scope**: 运动逻辑、动画系统、WebSocket 连接、多显示器支持

## §4 Interface Contract

### GDScript

```gdscript
# client/scripts/pet/pet_window.gd
class_name PetWindow extends Node2D

func set_mouse_passthrough(enabled: bool) -> void: ...
func get_pet_position() -> Vector2: ...
func set_pet_position(pos: Vector2) -> void: ...
```

### 场景结构

```
client/scenes/main.tscn        — 根场景，包含 CanvasLayer
client/scenes/pet/pet.tscn     — 桌宠精灵场景，包含 Sprite2D
```

### 资源文件

```
client/assets/placeholder/pet_idle.png  — 占位几何图形
```

## §5 Implementation Steps
1. 配置 `client/project.godot`：启用 `display/window` 透明背景、`always_on_top`、`borderless`、窗口尺寸匹配屏幕
2. 创建 `client/scenes/main.tscn` 作为根场景，包含 `CanvasLayer` 节点
3. 创建 `client/scenes/pet/pet.tscn`，包含 `Sprite2D` 节点（加载占位纹理）
4. 创建 `client/assets/placeholder/pet_idle.png` — 简单几何图形占位图
5. 创建 `client/scripts/pet/pet_window.gd` — 窗口管理脚本，实现穿透切换
6. 实现动态鼠标穿透：基于鼠标与桌宠精灵的距离判断是否启用穿透

## §6 Acceptance Criteria
- [ ] Godot 窗口背景透明，可以看到桌面
- [ ] 窗口始终在其他应用程序之上
- [ ] 鼠标点击可以穿透透明区域到达下层窗口
- [ ] 鼠标悬停在桌宠精灵上时可以正常交互（穿透被禁用）
- [ ] 桌宠占位精灵在桌面上可见
- [ ] 窗口覆盖整个主显示器区域

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
