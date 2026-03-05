# Phase 15: 跨平台适配

## §1 Goal
适配 macOS（沙盒权限/录屏授权引导）和 Linux（X11 + Wayland 截图/输入差异）。

## §2 Dependencies
- **Prerequisite phases**: Phase 09, Phase 03
- **Source files to read**: `server/src/lumina/vision/capture.py`, `server/src/lumina/tools/input_tools.py`, `client/project.godot`

## §3 Design & Constraints
- **Architecture principles**:
  - 平台检测模块：根据 OS 和显示服务器选择对应代码路径
  - macOS：引导用户授予 Screen Recording + Accessibility 权限；mss 不足时回退 CoreGraphics
  - Linux X11：mss 原生支持截图；输入模拟可回退 xdotool
  - Linux Wayland：截图通过 XDG Desktop Portal (D-Bus) 或 grim 实现；输入模拟通过 ydotool 或 libei
  - Godot：透明窗口行为因平台窗口合成器而异，需平台特定配置
  - 所有平台差异封装在统一接口之后，上层代码无需感知平台细节
- **Boundary conditions**:
  - macOS 权限检查使用系统 API（CGPreflightScreenCaptureAccess 等）
  - Linux Wayland 下 mss 和 pyautogui 均不可用，必须使用替代方案
  - 权限缺失时返回明确的用户引导说明（非静默失败）
  - PlatformInfo.permissions 动态检测，反映当前真实状态
  - Godot 导出设置需为每个平台单独配置（Info.plist for macOS 等）
- **Out of scope**: 移动平台、自定义 Wayland 合成器扩展

## §4 Interface Contract

```python
# server/src/lumina/platform/detector.py
from pydantic import BaseModel
from typing import Literal

class PlatformInfo(BaseModel):
    os: Literal["windows", "macos", "linux"]
    display_server: Literal["win32", "quartz", "x11", "wayland"] | None
    permissions: dict[str, bool]  # e.g., {"screen_capture": True, "accessibility": False}

class PlatformDetector:
    def detect(self) -> PlatformInfo:
        """检测当前操作系统和显示服务器类型。"""
        ...

    async def check_permissions(self) -> dict[str, bool]:
        """检查当前平台所需权限的授予状态。"""
        ...

    def get_permission_instructions(self) -> dict[str, str]:
        """返回每项缺失权限的用户引导说明文本。"""
        ...
```

```python
# server/src/lumina/platform/capture_adapter.py
from lumina.vision.capture import ScreenCapture

class CaptureAdapter:
    @staticmethod
    def get_capture_backend() -> ScreenCapture:
        """根据当前平台返回最佳截图后端实例。"""
        ...
```

```python
# server/src/lumina/platform/input_adapter.py

class InputAdapter:
    @staticmethod
    def get_input_backend() -> "InputSimulator":
        """根据当前平台返回最佳输入模拟后端实例。"""
        ...
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/platform/` 模块及 `__init__.py`
2. 创建 `server/src/lumina/platform/detector.py` — OS 和显示服务器检测
3. 创建 `server/src/lumina/platform/capture_adapter.py` — 平台特定截图后端选择
4. 创建 `server/src/lumina/platform/input_adapter.py` — 平台特定输入模拟后端选择
5. 实现 macOS 权限检查和用户引导对话框
6. 实现 Linux Wayland 截图（通过 XDG Desktop Portal D-Bus 接口）
7. 更新 Godot 项目导出设置，适配 macOS 和 Linux 平台
8. 创建 `server/tests/test_platform.py` — 基于 mock 的平台检测测试

## §6 Acceptance Criteria
- [ ] PlatformDetector 正确识别 OS 和显示服务器类型
- [ ] macOS：权限检查能发现缺失权限并提供引导说明
- [ ] Linux X11：截图和输入模拟通过现有后端正常工作
- [ ] Linux Wayland：通过 Portal 成功截图，通过 ydotool 成功模拟输入
- [ ] Godot 窗口在三个平台上均为透明
- [ ] 上层代码通过统一接口调用，无需平台判断逻辑
- [ ] 所有测试通过

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
