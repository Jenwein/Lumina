# Phase 07: 安全、隐私与多显示器

## §1 Goal

实现三大保护机制——高危操作拦截确认、应用黑名单/隐私遮罩、多显示器坐标映射——以及桌宠的对话气泡和右键菜单 UI，确保系统在功能强大的同时不会危害用户数据和隐私。

## §2 Dependencies

- **Prerequisite phases**: Phase 05 (`[x] Done`)
- **Reference Materials**:
    - [ ] [PRD — 安全与确认机制](../../../PRD.md) §4.2
    - [ ] [PRD — 隐私保护](../../../PRD.md) §4.4
    - [ ] [PRD — 多显示器支持](../../../PRD.md) §4.1
    - [ ] [PRD — UI 交互](../../../PRD.md) §2.3
- **Source files to read**:
    - [ ] `server/lumina/tools/base.py` (Phase 04 — RiskLevel)
    - [ ] `server/lumina/tools/registry.py` (Phase 04 — ToolRegistry.execute)
    - [ ] `server/lumina/vision/capture.py` (Phase 05 — ScreenCapture)
    - [ ] `server/lumina/ws/protocol.py` (Phase 01 — confirmation_request)
    - [ ] `client/scripts/pet/pet_controller.gd` (Phase 02)
    - [ ] `client/scripts/ws_client.gd` (Phase 01)

## §3 Design & Constraints

### 一、高危操作拦截

当 Agent 通过 ReAct 循环调用风险等级为 `HIGH` 的工具时，不直接执行，而是先通过桌宠向用户展示确认气泡：

```
Agent 调用 HIGH 风险工具
       │
       ▼
ToolRegistry.execute() 检测到 HIGH
       │
       ▼
Python: 发送 confirmation_request 消息
       │
       ├── payload: {
       │     "description": "即将删除文件 C:\\Users\\test.txt",
       │     "risk_level": "high",
       │     "request_id": "uuid"
       │   }
       │
       ▼
Godot: 桌宠显示醒目确认气泡
       │
       ├── [确认] 按钮 → 用户点击
       │     → 发送 user_action: {"action": "confirm", "request_id": "..."}
       │     → Python 端执行工具
       │
       └── [取消] 按钮 → 用户点击
             → 发送 user_action: {"action": "cancel", "request_id": "..."}
             → Python 端返回 "用户取消了此操作" 给 Agent
```

**确认超时**: 60s 内无响应自动取消。

**单步执行模式**: 用户可在设置中开启，此模式下所有工具调用（不仅 HIGH）都需确认。

### 二、隐私保护

#### 应用黑名单

用户配置不允许截图的应用列表。当黑名单应用处于前台时：

```yaml
# config.yaml
privacy:
  blacklist_apps:
    - "KeePass"
    - "1Password"
    - "银行"
  mask_regions: []    # 屏幕上的"不准看"矩形区域
```

- Python 端在每次 `capture_screen` 前检查前台窗口
- 若前台应用匹配黑名单，截图工具返回 "当前前台应用处于隐私保护中，无法截图"
- 使用 Windows API (`win32gui.GetForegroundWindow` + `win32process`) 获取前台应用名

#### 隐私遮罩

用户可定义屏幕上的矩形"禁看区域"：

- 截图后，在发送给 OCR/LLM 前对遮罩区域填充纯色
- 遮罩区域存储在配置文件中，支持运行时修改

### 三、多显示器支持

#### 坐标映射

Windows 多显示器使用统一虚拟坐标系（主显示器 (0,0) 在左上角，副显示器根据位置可能有负坐标）：

```python
# 示例: 双显示器布局
# 主显示器: (0, 0) - (1920, 1080)
# 副显示器 (左侧): (-1920, 0) - (0, 1080)
```

- Python 端使用 `screeninfo` 库获取所有显示器的几何信息
- 将显示器布局通过 `server_ready` 消息同步给 Godot
- Godot 窗口覆盖整个虚拟桌面，桌宠可跨屏移动

#### 新增消息

`server_ready` payload 扩展：

```json
{
  "version": "0.3.0",
  "capabilities": ["tools", "vision", "web"],
  "monitors": [
    {"id": 0, "x": 0, "y": 0, "width": 1920, "height": 1080, "is_primary": true},
    {"id": 1, "x": -1920, "y": 0, "width": 1920, "height": 1080, "is_primary": false}
  ]
}
```

### 四、桌宠 UI

#### 对话气泡

- 位于桌宠头顶，随桌宠移动
- 支持 Markdown 基础格式（粗体、代码块）的简单渲染
- 自动换行，最大宽度 300px
- 支持定时消失和手动关闭
- 确认气泡使用醒目的警告色（橙色/红色边框）

#### 右键菜单

右键点击桌宠弹出：

```
┌─────────────────────┐
│ 💬 对话窗口          │
│ 🔄 切换模型          │
│ ⚙️ 设置             │
│ 📋 查看日志          │
│ 🔒 单步模式 [✓]     │
│ ───────────────────  │
│ 🛑 紧急停止          │
└─────────────────────┘
```

- **紧急停止**: 立即终止当前 ReAct 循环，取消所有待执行操作
- **切换模型**: 弹出已配置模型列表
- **设置**: 打开设置面板（API 配置、隐私设置等）

### Out of scope

- 完整的设置面板 UI (Phase 08 打磨)
- macOS/Linux 平台的前台应用检测适配 (Phase 08)
- 详细的日志查看器 UI (Phase 08)

## §4 Interface Contract

### 安全拦截层

```python
# server/lumina/security/interceptor.py

class SecurityInterceptor:
    """在工具执行前进行安全检查的拦截层。"""

    def __init__(
        self,
        ws_server: "LuminaWSServer",
        step_mode: bool = False,
        confirmation_timeout: float = 60.0,
    ) -> None: ...

    async def check_and_execute(
        self, tool: "BaseTool", arguments: dict
    ) -> str:
        """检查风险等级，必要时请求用户确认后再执行。"""
        ...

    async def _request_confirmation(
        self, description: str, risk_level: str
    ) -> bool:
        """发送确认请求并等待用户响应。返回 True=确认, False=取消/超时。"""
        ...

    def set_step_mode(self, enabled: bool) -> None: ...


# server/lumina/security/emergency.py

class EmergencyStop:
    """紧急停止控制器。"""

    def __init__(self) -> None: ...

    def trigger(self) -> None:
        """触发紧急停止。"""
        ...

    def is_triggered(self) -> bool: ...
    def reset(self) -> None: ...
```

### 隐私保护

```python
# server/lumina/security/privacy.py
from dataclasses import dataclass


@dataclass
class MaskRegion:
    x: int
    y: int
    width: int
    height: int


class PrivacyGuard:
    """隐私保护模块 — 黑名单检查和遮罩。"""

    def __init__(
        self,
        blacklist_apps: list[str],
        mask_regions: list[MaskRegion],
    ) -> None: ...

    def is_foreground_blacklisted(self) -> bool:
        """检查当前前台应用是否在黑名单中。"""
        ...

    def get_foreground_app_name(self) -> str:
        """获取前台应用的进程名。"""
        ...

    def apply_mask(self, image: "Image.Image") -> "Image.Image":
        """在截图上应用隐私遮罩（纯色填充遮罩区域）。"""
        ...


# server/lumina/security/monitor_info.py

@dataclass
class MonitorInfo:
    id: int
    x: int
    y: int
    width: int
    height: int
    is_primary: bool


class MonitorManager:
    """多显示器信息管理。"""

    def get_all_monitors(self) -> list[MonitorInfo]: ...
    def get_primary(self) -> MonitorInfo: ...
    def point_to_monitor(self, x: int, y: int) -> MonitorInfo | None: ...
```

### Godot UI

```gdscript
# client/scripts/ui/speech_bubble.gd
class_name SpeechBubble
extends Control

signal closed

func show_message(text: String, duration: float = 0.0) -> void:
    ## duration=0 表示不自动关闭
    pass

func show_confirmation(
    description: String,
    risk_level: String,
    request_id: String
) -> void:
    ## 显示确认气泡，带确认/取消按钮
    pass

func hide_bubble() -> void: ...


# client/scripts/ui/context_menu.gd
class_name PetContextMenu
extends PopupMenu

signal emergency_stop_pressed
signal switch_model_requested
signal settings_requested
signal step_mode_toggled(enabled: bool)
signal log_viewer_requested

func _ready() -> void:
    ## 构建菜单项
    pass
```

## §5 Implementation Steps

1. **实现安全拦截层** (`server/lumina/security/interceptor.py`): 包装 `ToolRegistry.execute()`，在调用前检查风险等级，HIGH 风险发送确认请求并异步等待响应。
2. **实现紧急停止** (`server/lumina/security/emergency.py`): 全局停止标志，ReAct 循环每轮检查。
3. **实现隐私保护** (`server/lumina/security/privacy.py`): 前台应用检测 (win32gui)、隐私遮罩应用。修改 `CaptureScreenTool` 在截图前调用 `PrivacyGuard` 检查。
4. **实现多显示器管理** (`server/lumina/security/monitor_info.py`): 使用 `screeninfo` 获取显示器信息，在握手时同步给 Godot。
5. **安装依赖**: 添加 `pywin32`, `screeninfo` 到 `pyproject.toml`。
6. **实现对话气泡** (`client/scripts/ui/speech_bubble.gd`): 基于 `PanelContainer` + `RichTextLabel` + `AnimationPlayer`。
7. **实现确认气泡** (复用 `speech_bubble.gd`): 添加确认/取消按钮，醒目的警告样式。
8. **实现右键菜单** (`client/scripts/ui/context_menu.gd`): `PopupMenu` + 菜单项绑定信号。
9. **Godot 集成**: 在 `main.gd` 中处理 `confirmation_request` 消息并调用 `SpeechBubble.show_confirmation()`；处理菜单信号。
10. **扩展 Godot 窗口**: 根据多显示器信息调整窗口大小为虚拟桌面全尺寸。
11. **编写测试** (`server/tests/test_security.py`): 测试拦截逻辑、超时取消、黑名单检测、遮罩应用。

## §6 Acceptance Criteria

**⚠ MANDATORY: Every item must be verified and checked `[x]` before proceeding to §7.**

### Functional Verification — 安全拦截
- [ ] `SecurityInterceptor`: HIGH 风险工具调用时，Godot 显示醒目确认气泡
- [ ] 用户点击 [确认] 后工具正常执行并返回结果
- [ ] 用户点击 [取消] 后工具返回 "用户取消了此操作"
- [ ] 超时 60s 无响应后操作自动取消
- [ ] 单步模式 (`step_mode=True`) 下 LOW/MEDIUM/HIGH 所有工具调用都需确认
- [ ] `EmergencyStop.trigger()` 能立即终止当前 ReAct 循环

### Functional Verification — 隐私保护
- [ ] `PrivacyGuard.is_foreground_blacklisted()`: 黑名单应用在前台时返回 True
- [ ] 前台应用在黑名单中时 `inspect_window` / `capture_screen` 返回拒绝信息而非截图
- [ ] `PrivacyGuard.apply_mask()`: 隐私遮罩区域被纯色正确覆盖

### Functional Verification — 多显示器
- [ ] `MonitorManager.get_all_monitors()` 正确返回所有显示器信息 (位置、尺寸、主副)
- [ ] `server_ready` 消息中 `monitors` 字段包含完整显示器列表

### Functional Verification — Godot UI
- [ ] `SpeechBubble.show_message()` 显示对话气泡，随桌宠移动
- [ ] `SpeechBubble.show_confirmation()` 显示带确认/取消按钮的警告气泡
- [ ] 确认气泡的 [确认]/[取消] 按钮通过 WebSocket 正确发送 `user_action`
- [ ] 右键菜单弹出并包含所有菜单项 (对话/模型/设置/日志/单步/紧急停止)
- [ ] 右键菜单各项点击后发出对应信号

### Test Verification
- [ ] 单元测试 `pytest server/tests/test_security.py` 通过，0 failures
- [ ] 测试覆盖: 拦截逻辑、超时取消、黑名单检测、遮罩应用、紧急停止

### Integration Verification
- [ ] 端到端: Agent 调用 `delete_file` → Godot 显示确认气泡 → 用户确认 → 文件删除 → Agent 收到结果
- [ ] 端到端: 紧急停止按钮 → Agent 立即停止当前操作 → 桌宠回到 idle

### Code Quality
- [ ] `server/lumina/security/` 下所有文件无 linter 错误
- [ ] `client/scripts/ui/` 下所有文件无 GDScript 警告

## §7 State Teardown Checklist

**⚠ MANDATORY: Every item is a concrete action. Complete each one and check `[x]`.**

- [ ] **§3/§4 Updated**: 若实现中设计/接口有变，更新本文档 §3 和 §4 使其与最终代码一致
- [ ] **changelog.md**: 追加本阶段条目 (Delivered/Decisions/Deferred) → `../changelog.md`
- [ ] **api_registry/websocket_protocol.md**: 更新 `server_ready` 的 monitors 字段、新增 `emergency_stop` → `../api_registry/websocket_protocol.md`
- [ ] **api_registry/godot_ui.md**: 新增 `SpeechBubble`、`PetContextMenu` 组件和相关信号 → `../api_registry/godot_ui.md`
- [ ] **api_registry/tool_system.md**: 新增 `SecurityInterceptor`、`PrivacyGuard`、`MonitorManager` → `../api_registry/tool_system.md`
- [ ] **master_overview.md**: 将 Phase 07 状态改为 `[x] Done` → `../master_overview.md`
- [ ] **§2 checkboxes**: 将本文档 §2 中所有 Reference Materials 和 Source files 标记为 `[x]`
