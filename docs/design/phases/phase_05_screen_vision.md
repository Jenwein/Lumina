# Phase 05: 屏幕视觉与交互链路

## §1 Goal

实现屏幕截图、OCR 文字识别和 UI 元素检测能力，并构建"桌宠跑动到目标 → 播放点击动画 → 触发物理点击"的完整交互链路。本阶段完成后，Agent 能通过视觉感知屏幕内容，并指挥桌宠在屏幕上模拟人类操作。

## §2 Dependencies

- **Prerequisite phases**: Phase 02 (`[x] Done`), Phase 04 (`[x] Done`)
- **Reference Materials**:
    - [ ] [PRD — 全场景视觉模拟工具](../../../PRD.md) §2.2
    - [ ] [PRD — 桌宠跟随机制](../../../PRD.md) §2.3
    - [ ] [PRD — 按需 OCR](../../../PRD.md) §4.3
- **Source files to read**:
    - [ ] `server/lumina/tools/base.py` (Phase 04 — BaseTool)
    - [ ] `server/lumina/tools/registry.py` (Phase 04 — ToolRegistry)
    - [ ] `server/lumina/agent/core.py` (Phase 03 — AgentCore)
    - [ ] `client/scripts/pet/pet_controller.gd` (Phase 02 — 移动/状态)
    - [ ] `server/lumina/ws/protocol.py` (Phase 01 — 消息协议)

## §3 Design & Constraints

### 视觉感知管线

```
Agent 决定需要视觉信息
       │
       ▼
  截取屏幕截图 (mss)
       │
       ▼
  ┌────┴────────────┐
  │                 │
  ▼                 ▼
OCR 识别         UI 元素检测
(PaddleOCR)     (可选: 模板匹配/YOLO)
  │                 │
  └────┬────────────┘
       │
       ▼
  返回结构化结果给 Agent
  (文字位置、元素坐标)
       │
       ▼
  Agent 决定下一步操作
  (点击某坐标 / 输入文字 / 继续观察)
```

### 屏幕截图

- 使用 `mss` 库进行快速屏幕捕获（比 PIL.ImageGrab 快约 10 倍）
- 支持指定区域截图（减少 OCR 处理面积）
- 截图默认保存为内存中的 PIL Image，不写磁盘
- 支持多显示器截取（Phase 07 扩展坐标映射）

### OCR 方案

- 主方案: **PaddleOCR** — 开源、中英文支持好、本地运行无隐私风险
- 备选方案: pytesseract — 更轻量但中文识别质量较差
- OCR 返回格式: `list[OcrResult]`，每个包含文字、边界框坐标和置信度

### 物理交互模拟

使用 `pyautogui` 或 `pynput` 模拟鼠标/键盘操作：

| 操作 | 库 | 说明 |
|------|----|------|
| 鼠标移动 | pyautogui | `moveTo(x, y, duration)` |
| 单击/双击 | pyautogui | `click(x, y)` / `doubleClick(x, y)` |
| 拖拽 | pyautogui | `moveTo` + `mouseDown` + `moveTo` + `mouseUp` |
| 键盘输入 | pyautogui | `typewrite()` / `hotkey()` |
| 组合键 | pyautogui | `hotkey('ctrl', 'c')` |

### 交互链路 — "桌宠跑过去点击"

这是 Lumina 最核心的交互体验。当 Agent 决定点击屏幕某位置时：

```
Agent: "需要点击坐标 (800, 450)"
       │
       ▼
Python: 发送 pet_command: move_to(800, 450)
       │
       ▼
Godot: 桌宠开始跑向 (800, 450)
       │
       ▼
Godot: 到达目标 → 发送 arrived 事件 → 切换到 CLICKING 状态
       │
       ▼
Godot: 播放点击动画
       │
       ▼
Godot: 动画播放到"击中"帧 → 发送 click_ready 事件
       │
       ▼
Python: 收到 click_ready → 执行 pyautogui.click(800, 450)
       │
       ▼
Python: 发送 pet_command: set_state("celebrating" 或 "idle")
```

**新增消息类型 (C→S)**:

| type | payload | 说明 |
|------|---------|------|
| `pet_event` | `{"event": "arrived", "position": {"x": int, "y": int}}` | 桌宠到达目标位置 |
| `pet_event` | `{"event": "click_ready", "position": {"x": int, "y": int}}` | 点击动画到达击中帧 |
| `pet_event` | `{"event": "animation_finished", "animation": "..."}` | 动画播放完成 |

### 按需 OCR 策略

为避免不必要的性能开销，OCR 不持续运行：

1. Agent 在 ReAct 循环中判断是否需要视觉信息
2. 仅当 Agent 显式调用 `capture_screen` 或 `ocr_screen` 工具时才触发
3. 截图和 OCR 的结果作为 Observation 返回给 Agent

### Out of scope

- 多显示器坐标统一映射 (Phase 07)
- 隐私遮罩 / 黑名单应用拦截 (Phase 07)
- 高级图像理解 (VLM 多模态模型集成, 未来迭代)

## §4 Interface Contract

### 视觉工具

```python
# server/lumina/vision/capture.py
from dataclasses import dataclass
from PIL import Image


@dataclass
class ScreenRegion:
    x: int
    y: int
    width: int
    height: int


class ScreenCapture:
    def capture_full(self, monitor: int = 0) -> Image.Image:
        """截取指定显示器的全屏图像。"""
        ...

    def capture_region(self, region: ScreenRegion) -> Image.Image:
        """截取指定区域的图像。"""
        ...


# server/lumina/vision/ocr.py
from dataclasses import dataclass


@dataclass
class BoundingBox:
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)


@dataclass
class OcrResult:
    text: str
    bbox: BoundingBox
    confidence: float


class OcrEngine:
    def __init__(self, lang: str = "ch") -> None: ...

    def recognize(self, image: Image.Image) -> list[OcrResult]:
        """对图像执行 OCR，返回识别结果列表。"""
        ...

    def find_text(self, image: Image.Image, target: str) -> OcrResult | None:
        """在图像中查找特定文字，返回第一个匹配。"""
        ...


# server/lumina/vision/interaction.py

class PhysicalInteraction:
    """物理鼠标/键盘操作封装。"""

    async def click(self, x: int, y: int) -> None: ...
    async def double_click(self, x: int, y: int) -> None: ...
    async def right_click(self, x: int, y: int) -> None: ...
    async def drag(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None: ...
    async def type_text(self, text: str) -> None: ...
    async def hotkey(self, *keys: str) -> None: ...
    async def move_mouse(self, x: int, y: int, duration: float = 0.0) -> None: ...
```

### 视觉工具（注册到 ToolRegistry）

```python
# server/lumina/tools/vision_tools.py

class CaptureScreenTool(BaseTool):
    name = "capture_screen"
    description = "截取当前屏幕截图并进行 OCR 文字识别，返回识别到的所有文字及其在屏幕上的坐标位置。"
    parameters = {
        "type": "object",
        "properties": {
            "region": {
                "type": "object",
                "description": "可选的截图区域，不指定则截取全屏",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "width": {"type": "integer"},
                    "height": {"type": "integer"}
                }
            }
        },
        "required": []
    }
    risk_level = RiskLevel.LOW

    async def execute(self, region: dict | None = None) -> str: ...


class ClickAtTool(BaseTool):
    name = "click_at"
    description = "指挥桌宠跑到指定屏幕坐标并执行点击操作。桌宠会先移动到目标位置，播放点击动画，然后触发真实的鼠标点击。"
    parameters = {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "目标 X 坐标"},
            "y": {"type": "integer", "description": "目标 Y 坐标"},
            "click_type": {
                "type": "string",
                "enum": ["single", "double", "right"],
                "description": "点击类型，默认 single"
            }
        },
        "required": ["x", "y"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, x: int, y: int, click_type: str = "single") -> str: ...


class TypeTextTool(BaseTool):
    name = "type_text"
    description = "在当前焦点位置输入文字。"
    risk_level = RiskLevel.LOW

    async def execute(self, text: str) -> str: ...


class HotkeyTool(BaseTool):
    name = "hotkey"
    description = "执行键盘快捷键组合，如 Ctrl+C、Alt+F4 等。"
    risk_level = RiskLevel.MEDIUM

    async def execute(self, keys: list[str]) -> str: ...


class FindAndClickTool(BaseTool):
    name = "find_and_click"
    description = "在屏幕上查找指定文字并点击它。先截图+OCR定位文字，再指挥桌宠跑过去点击。"
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "要查找并点击的文字"}
        },
        "required": ["text"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, text: str) -> str: ...
```

### Godot 端扩展

```gdscript
# client/scripts/pet/pet_controller.gd (扩展)

signal click_ready(position: Vector2)   # 点击动画到击中帧时发出
signal action_completed                  # 整个动作序列完成

func perform_click_at(target: Vector2, speed: float = 300.0) -> void:
    ## 完整的"跑过去点击"流程: 移动 → 点击动画 → 发出 click_ready
    pass
```

## §5 Implementation Steps

1. **安装依赖**: 添加 `mss`, `paddleocr`, `paddlepaddle`, `pyautogui`, `Pillow` 到 `pyproject.toml`。
2. **实现屏幕截图模块** (`server/lumina/vision/capture.py`): 基于 `mss` 实现全屏和区域截图。
3. **实现 OCR 引擎** (`server/lumina/vision/ocr.py`): 封装 PaddleOCR，支持中英文识别和文字搜索。
4. **实现物理交互** (`server/lumina/vision/interaction.py`): 封装 `pyautogui` 的鼠标/键盘操作。
5. **实现视觉工具集** (`server/lumina/tools/vision_tools.py`): `CaptureScreenTool`, `ClickAtTool`, `TypeTextTool`, `HotkeyTool`, `FindAndClickTool`。
6. **扩展 WebSocket 协议**: 在 `protocol.py` 中添加 `pet_event` 消息类型。
7. **扩展 Godot 桌宠**: 在 `pet_controller.gd` 中添加 `perform_click_at()` 方法和 CLICKING 状态。实现点击动画，在关键帧通过 WebSocket 发送 `click_ready` 事件。
8. **实现 ClickAtTool 的协调逻辑**: Python 端发送 `move_to` → 等待 `click_ready` 事件 → 执行 `pyautogui.click` → 发送状态恢复指令。
9. **注册工具到 Agent**: 在启动时将所有视觉工具注册到 `ToolRegistry`。
10. **端到端测试**: 发送 "帮我打开记事本" → Agent 调用 `launch_app` → "在记事本中输入 Hello" → Agent 调用 `capture_screen` 定位记事本 → `click_at` 点击编辑区 → `type_text` 输入文字。

## §6 Acceptance Criteria

- [ ] `ScreenCapture.capture_full()` 返回正确的屏幕截图 PIL Image
- [ ] `OcrEngine.recognize()` 能识别屏幕上的中英文文字并返回正确的边界框坐标
- [ ] `OcrEngine.find_text()` 能在屏幕中定位指定文字
- [ ] `PhysicalInteraction.click()` 能在指定坐标触发真实鼠标点击
- [ ] `ClickAtTool` 完整链路: 桌宠移动 → 到达 → 点击动画 → 物理点击 → 恢复 idle
- [ ] `FindAndClickTool` 能自动截图、OCR 定位文字、驱动桌宠点击
- [ ] 桌宠在执行视觉分析时切换到 OBSERVING 状态
- [ ] `pytest server/tests/test_vision.py` 全部通过

## §7 State Teardown Checklist

- [ ] **Phase Document Updated** (if design changed during implementation)
- [ ] `changelog.md` updated
- [ ] `api_registry/tool_system.md` updated (新增视觉工具)
- [ ] `api_registry/websocket_protocol.md` updated (新增 `pet_event`)
- [ ] `api_registry/godot_ui.md` updated (新增 CLICKING 状态和 `click_ready` 信号)
- [ ] `master_overview.md` Phase 05 status set to `[x] Done`
