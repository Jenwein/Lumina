# Phase 17: 隐私保护

## §1 Goal
实现黑名单应用检测（前台时自动禁用截图）和用户自定义隐私遮罩区域。

## §2 Dependencies
- **Prerequisite phases**: Phase 09, Phase 16
- **Source files to read**: `server/src/lumina/vision/capture.py`, `server/src/lumina/config/`

## §3 Design & Constraints
- **Architecture principles**:
  - Blacklist 机制：用户配置应用名称/窗口标题列表（如银行客户端、密码管理器）
  - 当黑名单应用位于前台时，Agent 自动禁用截图能力
  - 前台应用检测：平台特定实现（Win32 API `GetForegroundWindow`、macOS AppleScript、Linux xdotool/xprop）
  - Privacy mask：用户定义矩形屏幕区域，截图时该区域永远不被捕获（涂黑或排除）
  - 遮罩在截图后、发送至 OCR 或 LLM 前应用
  - 配置持久化于 YAML 文件中，与其他设置统一管理
- **Boundary conditions**:
  - 前台检测频率不超过每秒一次，避免资源浪费
  - 黑名单匹配支持子串和通配符
  - 遮罩坐标使用绝对像素值，多显示器场景下以主显示器为基准
- **Out of scope**: 遮罩区域的 OCR 处理、按显示器独立黑名单、数据泄露防护（DLP）

## §4 Interface Contract

```python
# server/src/lumina/privacy/guard.py
from PIL import Image
from pydantic import BaseModel

class PrivacyConfig(BaseModel):
    blacklisted_apps: list[str] = []
    mask_regions: list[tuple[int, int, int, int]] = []  # (x, y, w, h)

class PrivacyGuard:
    def __init__(self, config: PrivacyConfig) -> None: ...
    def is_capture_allowed(self) -> bool: ...
    def get_foreground_app(self) -> str: ...
    def apply_masks(self, image: Image.Image) -> Image.Image: ...
```

**异常类型**:
```python
# server/src/lumina/privacy/exceptions.py
class PrivacyBlockedError(Exception):
    """当黑名单应用在前台时抛出，阻止截图操作"""
    pass
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/privacy/` 模块（含 `__init__.py`）
2. 创建 `server/src/lumina/privacy/guard.py` — 实现 `PrivacyGuard`，包含前台应用检测逻辑
3. 实现平台特定的前台应用检测（Win32 `ctypes` / macOS `subprocess` AppleScript / Linux `subprocess` xdotool）
4. 实现遮罩覆盖：对捕获图像中的指定矩形区域进行涂黑处理
5. 将 `PrivacyGuard` 集成到 `ScreenCapture` 管道中（截图前检查黑名单，截图后应用遮罩）
6. 在设置 UI 中添加隐私配置区段（作为 Phase 14 的扩展）
7. 创建 `server/tests/test_privacy.py` — 测试黑名单匹配和遮罩应用

## §6 Acceptance Criteria
- [ ] 黑名单应用在前台时，截图返回 `PrivacyBlockedError`
- [ ] 非黑名单应用在前台时，截图正常工作
- [ ] 遮罩区域在截图中被正确涂黑
- [ ] 配置从 YAML 正确加载
- [ ] 所有测试通过

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
