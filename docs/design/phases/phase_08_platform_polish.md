# Phase 08: 跨平台适配、UI 打磨与发布

## §1 Goal

完成 macOS 和 Linux 平台适配，实现多模型配置界面，打磨桌宠动画和交互体验，进行资源优化（低功耗模式），编写用户文档，最终达到 V1.0 发布标准。

## §2 Dependencies

- **Prerequisite phases**: Phase 07 (`[x] Done`)
- **Reference Materials**:
    - [ ] [PRD — 跨平台方案](../../../PRD.md) §3
    - [ ] [PRD — 资源优化](../../../PRD.md) §4.3
    - [ ] [PRD — 模型资产计划](../../../PRD.md) §4.5
    - [ ] [PRD — 开发里程碑 V0.4 & V1.0](../../../PRD.md) §5
    - [ ] [Godot 导出模板文档](../../godot/godot-docs/tutorials/export/index.rst)
- **Source files to read**:
    - [ ] 全部已有源码（最终集成阶段）

## §3 Design & Constraints

### 一、跨平台适配

#### macOS 适配

| 挑战 | 解决方案 |
|------|---------|
| 沙盒限制 | 引导用户授权辅助功能、屏幕录制权限，提供权限检查 UI |
| 截图权限 | 首次使用截图工具时弹出系统授权对话框，检测授权状态并提示 |
| 前台应用检测 | 使用 `NSWorkspace` (通过 `pyobjc`) 替代 `win32gui` |
| 透明窗口 | Godot 原生支持 macOS 透明窗口 |
| 键盘模拟 | `pyautogui` 跨平台兼容，需处理 Cmd vs Ctrl 差异 |

#### Linux 适配

| 挑战 | 解决方案 |
|------|---------|
| X11 截图 | `mss` 原生支持 |
| Wayland 截图 | 使用 XDG Desktop Portal (`dbus` 接口) 或管道流 |
| 前台应用检测 | X11: `python-xlib`; Wayland: 通过 D-Bus 接口 |
| 透明窗口 | 需要支持合成器 (compositor) 的桌面环境 |
| 输入模拟 | Wayland 下 `pyautogui` 受限，可能需要 `ydotool` |

#### 平台抽象层

```
server/lumina/platform/
├── __init__.py
├── base.py         # 平台操作抽象接口
├── windows.py      # Windows 实现
├── macos.py        # macOS 实现
└── linux.py        # Linux 实现
```

根据运行平台自动加载对应实现：

```python
# server/lumina/platform/__init__.py
import sys

def get_platform() -> "PlatformAdapter":
    if sys.platform == "win32":
        from .windows import WindowsPlatform
        return WindowsPlatform()
    elif sys.platform == "darwin":
        from .macos import MacOSPlatform
        return MacOSPlatform()
    else:
        from .linux import LinuxPlatform
        return LinuxPlatform()
```

### 二、多模型配置界面

在 Godot 端实现设置面板，支持：

- 查看/添加/编辑/删除 API 配置 (名称、API Base、API Key、模型名)
- 切换当前活跃模型
- 测试连接 ("发送一条测试消息")
- 配置保存到本地 `config.yaml`

**通信方式**: 通过 WebSocket 新增 `config_*` 系列消息：

| type (C→S) | payload | 说明 |
|------------|---------|------|
| `config_get` | `{}` | 请求当前配置 |
| `config_update` | `{"models": [...], "active_model": "..."}` | 更新配置 |
| `config_test_model` | `{"model_name": "..."}` | 测试指定模型连接 |

| type (S→C) | payload | 说明 |
|------------|---------|------|
| `config_data` | `{完整配置 JSON}` | 返回当前配置 |
| `config_test_result` | `{"model_name": "...", "success": bool, "message": "..."}` | 测试结果 |

### 三、动画打磨

| 动画 | 帧数建议 | 触发条件 |
|------|---------|---------|
| idle_breathe | 6-8帧 | 默认待机 |
| idle_blink | 4帧 | 随机触发 |
| walk | 6-8帧 | 移动中 |
| think | 4-6帧 | Agent 思考中 |
| type | 4帧 | 输入文字中 |
| observe | 4帧 | 屏幕分析中 |
| click | 6帧 | 执行点击 |
| celebrate | 8帧 | 任务成功 |
| fail | 6帧 | 任务失败 |
| wave | 6帧 | 首次打招呼 |

### 四、资源优化

| 优化 | 措施 |
|------|------|
| **低功耗模式** | 桌宠闲置 30s 后将帧率从 60fps 降至 10fps |
| **按需 OCR** | 仅 Agent 显式请求时触发（已在 Phase 05 实现） |
| **内存管理** | PaddleOCR 模型延迟加载，首次调用时初始化 |
| **浏览器清理** | Playwright 浏览器闲置自动关闭（已在 Phase 06 实现） |
| **日志轮转** | 日志文件大小限制 + 自动轮转 |

### 五、分发打包

| 平台 | Python 打包 | Godot 导出 |
|------|------------|-----------|
| Windows | PyInstaller → `.exe` | Godot Export → `.exe` |
| macOS | PyInstaller → `.app` | Godot Export → `.app` |
| Linux | PyInstaller → binary | Godot Export → binary |

提供一键启动脚本：启动 Python 服务 → 等待就绪 → 启动 Godot 客户端。

### Out of scope

- 自动更新机制
- 安装程序制作 (NSIS/DMG)
- 应用商店上架
- Spine/Live2D/VRM 高级模型集成（列入未来路线图）

## §4 Interface Contract

### 平台抽象

```python
# server/lumina/platform/base.py
from abc import ABC, abstractmethod
from PIL import Image


class PlatformAdapter(ABC):
    @abstractmethod
    def get_foreground_app_name(self) -> str:
        """获取前台应用进程名。"""
        ...

    @abstractmethod
    def get_monitors(self) -> list["MonitorInfo"]:
        """获取所有显示器信息。"""
        ...

    @abstractmethod
    def capture_screen(self, monitor_id: int = 0) -> Image.Image:
        """截取指定显示器屏幕。"""
        ...

    @abstractmethod
    def check_accessibility_permission(self) -> bool:
        """检查是否有辅助功能权限（macOS）。Windows/Linux 返回 True。"""
        ...

    @abstractmethod
    def check_screen_capture_permission(self) -> bool:
        """检查是否有屏幕录制权限。"""
        ...
```

### Godot 设置面板

```gdscript
# client/scripts/ui/settings_panel.gd
class_name SettingsPanel
extends Control

signal config_changed(config: Dictionary)
signal model_test_requested(model_name: String)

func load_config(config: Dictionary) -> void:
    ## 从服务端配置数据填充 UI
    pass

func _on_save_pressed() -> void:
    ## 收集表单数据，通过 WebSocket 发送 config_update
    pass

func _on_test_pressed() -> void:
    ## 发送 config_test_model
    pass

func show_test_result(model_name: String, success: bool, message: String) -> void:
    ## 显示测试结果
    pass
```

### 资源优化

```gdscript
# client/scripts/performance_manager.gd
class_name PerformanceManager
extends Node

var idle_timer: float = 0.0
var low_power_mode: bool = false
var idle_threshold: float = 30.0
var normal_fps: int = 60
var low_power_fps: int = 10

func _process(delta: float) -> void:
    ## 检测闲置时间，自动切换低功耗模式
    pass

func enter_low_power() -> void:
    Engine.max_fps = low_power_fps
    low_power_mode = true

func exit_low_power() -> void:
    Engine.max_fps = normal_fps
    low_power_mode = false
```

## §5 Implementation Steps

1. **实现平台抽象层**: 创建 `server/lumina/platform/` 模块，定义 `PlatformAdapter` 接口。
2. **实现 Windows 适配**: 将现有 `win32gui` 相关代码迁移到 `WindowsPlatform`。
3. **实现 macOS 适配**: 使用 `pyobjc` 实现前台应用检测和权限检查。
4. **实现 Linux 适配**: X11 (python-xlib) 和 Wayland (D-Bus) 双路径。
5. **重构现有代码**: `PrivacyGuard`, `ScreenCapture` 等使用 `PlatformAdapter` 替代直接平台调用。
6. **实现多模型配置消息**: 在 WebSocket 协议中添加 `config_*` 消息类型。
7. **实现 Godot 设置面板** (`client/scripts/ui/settings_panel.gd`): 模型管理 UI。
8. **制作正式美术资源**: 替换占位符 SpriteSheet，制作完整动画集。
9. **实现低功耗模式** (`client/scripts/performance_manager.gd`): 闲置降帧。
10. **实现 PaddleOCR 延迟加载**: 首次调用时初始化，减少启动时间。
11. **配置打包流程**: PyInstaller 配置 + Godot 导出模板。
12. **编写一键启动脚本**: `start_lumina.bat` (Windows) / `start_lumina.sh` (Unix)。
13. **编写用户文档**: 安装指南、快速上手、常见问题。
14. **全面测试**: 各平台端到端测试。

## §6 Acceptance Criteria

- [ ] Windows 上完整功能正常运行
- [ ] macOS 上完成权限引导，截图和交互正常（需 macOS 环境测试）
- [ ] Linux X11 上截图和交互正常
- [ ] 多模型配置面板可添加/编辑/删除 API 配置
- [ ] 切换模型后 Agent 使用新模型回复
- [ ] 测试连接功能正确反馈成功/失败
- [ ] 桌宠闲置 30s 后帧率降至 10fps，有交互时恢复 60fps
- [ ] PaddleOCR 首次调用延迟加载
- [ ] 一键启动脚本可正常启动完整系统
- [ ] 用户文档完整覆盖安装和使用流程

## §7 State Teardown Checklist

- [ ] **Phase Document Updated** (if design changed during implementation)
- [ ] `changelog.md` updated
- [ ] 所有 `api_registry/` 文件最终审查更新
- [ ] `master_overview.md` Phase 08 status set to `[x] Done`, overall status → Completed
