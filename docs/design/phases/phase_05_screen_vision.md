# Phase 05: 屏幕视觉与交互链路

## §1 Goal

构建**三级感知策略** (UI Automation → OCR → AI 视觉分析) 实现对桌面应用的精准识别与操控，采用**活动窗口聚焦截图**和**比例坐标系**确保跨分辨率稳定性、降低 AI 依赖和 token 开销，并完成"桌宠跑动到目标 → 播放点击动画 → 触发物理点击"的完整交互链路。

## §2 Dependencies

- **Prerequisite phases**: Phase 02 (`[x] Done`), Phase 04 (`[x] Done`)
- **Reference Materials**:
    - [ ] [PRD — 全场景视觉模拟工具](../../../PRD.md) §2.2
    - [ ] [PRD — 桌宠跟随机制](../../../PRD.md) §2.3
    - [ ] [PRD — 按需 OCR](../../../PRD.md) §4.3
    - [ ] [Windows UI Automation 文档](https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32)
- **Source files to read**:
    - [ ] `server/lumina/tools/base.py` (Phase 04 — BaseTool, RiskLevel)
    - [ ] `server/lumina/tools/registry.py` (Phase 04 — ToolRegistry)
    - [ ] `server/lumina/agent/core.py` (Phase 03 — AgentCore)
    - [ ] `client/scripts/pet/pet_controller.gd` (Phase 02 — 移动/状态)
    - [ ] `server/lumina/ws/protocol.py` (Phase 01 — 消息协议)

## §3 Design & Constraints

### 核心设计理念

1. **最小化 AI 依赖**: 用户可接入能力参差不齐的 AI 模型（从 glm-4-flash 到 GPT-4o），系统必须在 AI 视觉能力有限时仍能稳定工作。
2. **活动窗口聚焦**: 不做全屏截图，仅截取目标应用的活动窗口区域，减少信息噪声、提高识别精度、降低 token 开销。
3. **比例坐标系**: AI 返回的定位结果统一为 `(rx, ry)` 比例值 (0.0~1.0)，系统根据实际窗口位置/尺寸换算为屏幕绝对像素坐标。

### 三级感知策略

```
Agent 需要操作某应用
       │
       ▼
  激活目标窗口 / 获取活动窗口信息
  (进程名、窗口标题、位置、尺寸)
       │
       ▼
  ┌──────────────────────────────────────────────┐
  │ Tier 1: UI Automation (最快、最准、零成本)     │
  │                                              │
  │ 通过 Windows UIA 扫描窗口 UI 元素树           │
  │ 获取按钮/输入框/菜单/图标的:                  │
  │   - 名称 (Name)                              │
  │   - 类型 (ControlType: Button, Edit, etc.)   │
  │   - 边界矩形 (BoundingRectangle)             │
  │   - 可用状态 (IsEnabled)                      │
  │   - 自动化ID (AutomationId)                  │
  │                                              │
  │ 返回结构化元素列表 → AI 按名称选择目标元素     │
  └────────┬─────────────────────────────────────┘
           │
           ├── 找到目标元素 → 边界矩形转比例坐标 → 换算屏幕像素 → 执行操作
           │
           ├── 元素树不完整 / 找不到目标 → Tier 2
           │
           ▼
  ┌──────────────────────────────────────────────┐
  │ Tier 2: OCR 文本提取 (快速、低成本)           │
  │                                              │
  │ 仅截取活动窗口区域 (mss)                      │
  │ PaddleOCR 提取所有文字 + 边界框               │
  │ 序列化为结构化文本:                           │
  │   "发送 按钮 位置:(0.85, 0.92)"              │
  │   "搜索 输入框 位置:(0.50, 0.05)"            │
  │                                              │
  │ 将序列化结果(纯文本)发给 AI                   │
  │ AI 返回目标的比例坐标 (rx, ry)                │
  └────────┬─────────────────────────────────────┘
           │
           ├── AI 成功定位 → 比例坐标换算 → 执行操作
           │
           ├── 文字信息不足以定位 (图标、无标签控件等) → Tier 3
           │
           ▼
  ┌──────────────────────────────────────────────┐
  │ Tier 3: AI 视觉分析 (兜底、高成本)            │
  │                                              │
  │ 将活动窗口截图(适当缩放)发送给 AI             │
  │ 结合 Tier 2 的 OCR 数据提供上下文             │
  │ AI 返回目标的比例坐标 (rx, ry)                │
  │                                              │
  │ 适用: 图标、无文字按钮、复杂自绘UI            │
  └──────────────────────────────────────────────┘
```

### 比例坐标系与换算

AI 和各识别层统一使用**相对于活动窗口的比例坐标** `(rx, ry)`，取值范围 `[0.0, 1.0]`：

```
活动窗口
┌──────────────────────────┐
│(0.0, 0.0)    (1.0, 0.0)  │
│                          │
│        (rx, ry)          │  ← AI 返回的比例位置
│           ●              │
│                          │
│(0.0, 1.0)    (1.0, 1.0)  │
└──────────────────────────┘
```

**换算公式**:

```
窗口信息: window_x, window_y, window_width, window_height (屏幕像素)

screen_x = window_x + rx * window_width
screen_y = window_y + ry * window_height
```

**优势**:
- 截图缩放不影响结果：无论图片从 1920x1080 缩到 960x540 发给 AI，比例值不变
- AI 模型无需知道实际分辨率，降低推理难度
- 跨分辨率/DPI 天然兼容

### 活动窗口管理

操作任何应用前，先确保目标为活动窗口：

```python
# 操作流程
1. 通过进程名/窗口标题查找目标窗口句柄
2. 调用 SetForegroundWindow() 激活窗口
3. 获取窗口矩形: GetWindowRect() → (x, y, width, height)
4. 所有后续操作基于此窗口矩形进行
```

### Tier 1 — UI Automation 详细设计

Windows UIA 通过 COM 接口提供应用的 UI 元素树。Python 可通过 `uiautomation` 库或 `comtypes` 访问。

**扫描返回的元素结构**:

```python
@dataclass
class UIElement:
    name: str                    # 元素名称 (如 "发送", "搜索框")
    control_type: str            # 控件类型 (Button, Edit, MenuItem, etc.)
    automation_id: str           # 开发者设定的自动化ID
    bounding_rect: Rect          # 屏幕绝对像素矩形
    is_enabled: bool             # 是否可交互
    children_count: int          # 子元素数量
```

**序列化为 AI 可读文本**:

```
[窗口元素列表 — 记事本]
1. [Button] "文件(F)" 位置:(0.02, 0.02) 可用
2. [Button] "编辑(E)" 位置:(0.08, 0.02) 可用
3. [Edit] "文本编辑器" 位置:(0.50, 0.52) 可用
4. [StatusBar] "第 1 行, 第 1 列" 位置:(0.50, 0.97) 可用
```

**UIA 的适用范围与局限**:
- 适用: 原生 Win32、WPF、WinForms、大部分 UWP 应用
- 部分适用: Electron (Chromium 内置了部分无障碍支持)
- 不适用: 游戏、部分自绘 UI 框架、未暴露无障碍树的自定义控件

### Tier 2 — OCR 文本提取详细设计

当 UIA 无法覆盖时，回退到 OCR：

1. 使用 `mss` **仅截取活动窗口矩形区域**
2. 截图缩放策略: 长边不超过 1280px（平衡 OCR 精度与速度）
3. PaddleOCR 识别所有文字，返回文字内容 + 在截图中的像素边界框
4. 将像素边界框转换为比例坐标 (相对窗口)
5. 序列化为 AI 可读的纯文本列表（不发图片）
6. AI 根据纯文本列表推理目标位置，返回比例坐标 `(rx, ry)`

**序列化格式示例**:

```
[活动窗口 OCR 结果 — 微信 (1200x800)]
文字识别:
1. "文件" 位置:(0.03, 0.01) 置信度:0.98
2. "聊天" 位置:(0.05, 0.12) 置信度:0.97
3. "通讯录" 位置:(0.05, 0.18) 置信度:0.96
4. "发送" 位置:(0.88, 0.93) 置信度:0.99
5. "表情" 位置:(0.72, 0.93) 置信度:0.95

请问你要操作哪个元素？请返回其比例坐标 (rx, ry)。
```

### Tier 3 — AI 视觉分析详细设计

当目标元素无文字标识（图标、无标签按钮等），需要 AI 看图：

1. 将活动窗口截图缩放至长边不超过 **768px**（控制 token 成本）
2. 连同 Tier 2 的 OCR 文本数据一起发给 AI（多模态请求）
3. AI 结合截图和文本数据，返回目标比例坐标
4. **回退条件**: 仅当 Tier 1 和 Tier 2 均无法定位时才触发

**注意**: 此 Tier 依赖 AI 模型的多模态能力（图像理解）。若用户配置的模型不支持图像输入，工具返回提示信息告知用户需要手动操作或切换到支持视觉的模型。

### 物理交互模拟

使用 `pyautogui` 模拟鼠标/键盘操作：

| 操作 | 方法 | 说明 |
|------|------|------|
| 鼠标移动 | `moveTo(x, y, duration)` | 平滑移动 |
| 单击/双击 | `click(x, y)` / `doubleClick(x, y)` | 精准定点 |
| 右键 | `rightClick(x, y)` | 右键菜单 |
| 拖拽 | `mouseDown` → `moveTo` → `mouseUp` | 拖放操作 |
| 键盘输入 | `typewrite()` / `write()` | 文字输入 |
| 组合键 | `hotkey('ctrl', 'c')` | 快捷键 |

### 交互链路 — "桌宠跑过去点击"

当 Agent 通过三级识别确定目标后，触发完整的交互链路：

```
Agent: "需要点击活动窗口中比例坐标 (0.85, 0.92) 的元素"
       │
       ▼
Python: 换算为屏幕绝对坐标
        screen_x = window_x + 0.85 * window_w  → 例如 1020
        screen_y = window_y + 0.92 * window_h  → 例如 826
       │
       ▼
Python: 发送 pet_command: move_to(1020, 826)
       │
       ▼
Godot: 桌宠开始跑向 (1020, 826)
       │
       ▼
Godot: 到达目标 → 发送 pet_event: arrived
       │
       ▼
Godot: 切换到 CLICKING 状态，播放点击动画
       │
       ▼
Godot: 动画播放到"击中"帧 → 发送 pet_event: click_ready
       │
       ▼
Python: 收到 click_ready → 执行 pyautogui.click(1020, 826)
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

### 按需触发策略

所有识别操作按需触发，不持续运行：

1. Agent 在 ReAct 循环中判断需要操作某应用
2. 调用 `inspect_window` 工具 → 触发三级识别
3. 获得元素列表后，Agent 选择目标元素调用 `click_at` 或 `type_in_element`
4. 操作完成后可再次 `inspect_window` 验证结果

### Out of scope

- 多显示器坐标统一映射 (Phase 07)
- 隐私遮罩 / 黑名单应用拦截 (Phase 07)
- macOS/Linux 平台的 UIA 替代方案 (Phase 08, macOS: NSAccessibility, Linux: AT-SPI)

## §4 Interface Contract

### 活动窗口管理

```python
# server/lumina/vision/window_info.py
from dataclasses import dataclass


@dataclass
class WindowRect:
    x: int              # 窗口左上角屏幕 X
    y: int              # 窗口左上角屏幕 Y
    width: int          # 窗口宽度
    height: int         # 窗口高度


@dataclass
class WindowInfo:
    hwnd: int                   # 窗口句柄
    title: str                  # 窗口标题
    process_name: str           # 进程名
    rect: WindowRect            # 窗口矩形
    is_foreground: bool         # 是否为前台窗口


class WindowManager:
    """活动窗口管理：查找、激活、获取信息。"""

    def get_foreground_window(self) -> WindowInfo:
        """获取当前前台窗口信息。"""
        ...

    def find_window(self, title: str | None = None, process: str | None = None) -> WindowInfo | None:
        """按标题或进程名查找窗口。"""
        ...

    def activate_window(self, hwnd: int) -> bool:
        """将指定窗口设为前台。"""
        ...

    def get_window_rect(self, hwnd: int) -> WindowRect:
        """获取窗口矩形。"""
        ...
```

### 比例坐标转换

```python
# server/lumina/vision/coordinates.py
from dataclasses import dataclass


@dataclass
class RatioPoint:
    """相对于活动窗口的比例坐标 (0.0~1.0)。"""
    rx: float
    ry: float


@dataclass
class ScreenPoint:
    """屏幕绝对像素坐标。"""
    x: int
    y: int


class CoordinateConverter:
    """比例坐标 ↔ 屏幕像素坐标 的双向转换。"""

    @staticmethod
    def ratio_to_screen(ratio: RatioPoint, window: "WindowRect") -> ScreenPoint:
        """比例坐标 → 屏幕绝对像素。"""
        return ScreenPoint(
            x=int(window.x + ratio.rx * window.width),
            y=int(window.y + ratio.ry * window.height),
        )

    @staticmethod
    def screen_to_ratio(point: ScreenPoint, window: "WindowRect") -> RatioPoint:
        """屏幕绝对像素 → 比例坐标。"""
        return RatioPoint(
            rx=(point.x - window.x) / window.width,
            ry=(point.y - window.y) / window.height,
        )

    @staticmethod
    def bbox_to_ratio_center(
        bbox_x: int, bbox_y: int, bbox_w: int, bbox_h: int,
        image_width: int, image_height: int,
    ) -> RatioPoint:
        """OCR/UIA 边界框像素 → 比例坐标(中心点)。"""
        center_x = bbox_x + bbox_w / 2
        center_y = bbox_y + bbox_h / 2
        return RatioPoint(
            rx=center_x / image_width,
            ry=center_y / image_height,
        )
```

### Tier 1 — UI Automation

```python
# server/lumina/vision/ui_automation.py
from dataclasses import dataclass


@dataclass
class UIElement:
    name: str                       # 元素显示名称
    control_type: str               # Button, Edit, MenuItem, CheckBox, etc.
    automation_id: str              # 自动化ID
    bounding_rect: tuple[int, int, int, int]  # (x, y, width, height) 屏幕像素
    is_enabled: bool                # 是否可交互
    value: str | None = None        # 当前值 (输入框的文字等)
    children_count: int = 0


class UIAutomationScanner:
    """通过 Windows UI Automation 扫描窗口元素树。"""

    def scan_window(self, hwnd: int, max_depth: int = 5) -> list[UIElement]:
        """扫描指定窗口的 UI 元素树，返回可交互元素列表。
        max_depth 控制递归深度，避免过深的元素树导致性能问题。
        """
        ...

    def find_element(self, hwnd: int, name: str = "", control_type: str = "") -> UIElement | None:
        """在窗口中查找指定名称/类型的元素。"""
        ...

    def serialize_for_llm(
        self, elements: list[UIElement], window_rect: "WindowRect"
    ) -> str:
        """将元素列表序列化为 AI 可读的纯文本。
        边界矩形自动转为相对窗口的比例坐标。

        输出示例:
        [窗口元素 — 记事本]
        1. [Button] "文件(F)" 位置:(0.02, 0.02) 可用
        2. [Edit] "文本编辑区" 位置:(0.50, 0.52) 可用
        """
        ...

    @staticmethod
    def is_available() -> bool:
        """检查 UIA 是否可用 (仅 Windows)。"""
        ...
```

### Tier 2 — OCR

```python
# server/lumina/vision/capture.py
from dataclasses import dataclass
from PIL import Image


class ScreenCapture:
    """基于 mss 的屏幕截图，支持活动窗口区域截取。"""

    def capture_window(self, window_rect: "WindowRect", max_long_edge: int = 1280) -> Image.Image:
        """截取活动窗口区域并按比例缩放。
        max_long_edge 控制缩放上限，平衡精度与性能。
        """
        ...

    def capture_window_for_ai(self, window_rect: "WindowRect", max_long_edge: int = 768) -> Image.Image:
        """截取活动窗口区域，缩放到适合发送给 AI 的尺寸。"""
        ...

    def capture_full(self, monitor: int = 0) -> Image.Image:
        """截取指定显示器全屏 (仅用于特殊场景)。"""
        ...


# server/lumina/vision/ocr.py
from dataclasses import dataclass


@dataclass
class OcrResult:
    text: str
    bbox_x: int             # 在截图中的像素位置
    bbox_y: int
    bbox_width: int
    bbox_height: int
    confidence: float
    ratio_center: "RatioPoint"   # 相对窗口的比例坐标(中心点)


class OcrEngine:
    """PaddleOCR 封装，延迟加载模型。"""

    def __init__(self, lang: str = "ch") -> None:
        self._engine = None  # 首次调用时初始化

    def recognize(self, image: Image.Image, image_width: int, image_height: int) -> list[OcrResult]:
        """对图像执行 OCR，返回结果列表(含比例坐标)。"""
        ...

    def serialize_for_llm(self, results: list[OcrResult], window_title: str) -> str:
        """将 OCR 结果序列化为 AI 可读的纯文本。

        输出示例:
        [活动窗口 OCR — 微信]
        1. "文件" 位置:(0.03, 0.01) 置信度:0.98
        2. "发送" 位置:(0.88, 0.93) 置信度:0.99
        """
        ...
```

### Tier 3 — AI 视觉分析

```python
# server/lumina/vision/ai_visual.py

class AIVisualAnalyzer:
    """将窗口截图发送给 AI 进行视觉定位的兜底方案。"""

    def __init__(self, llm_client: "LLMClient") -> None: ...

    async def locate_element(
        self,
        image: "Image.Image",
        description: str,
        ocr_context: str = "",
    ) -> "RatioPoint | None":
        """请求 AI 在截图中定位指定元素，返回比例坐标。
        
        Args:
            image: 活动窗口截图 (已缩放)
            description: 要定位的元素描述 (如 "设置图标", "关闭按钮")
            ocr_context: Tier 2 提供的 OCR 文本上下文
        
        Returns:
            比例坐标，或 None (AI不支持图像/无法定位)
        """
        ...

    def check_multimodal_support(self) -> bool:
        """检查当前 LLM 是否支持图像输入。"""
        ...
```

### 感知编排器

```python
# server/lumina/vision/perceiver.py

@dataclass
class PerceptionResult:
    """三级感知的统一输出。"""
    tier_used: int                          # 1, 2, 3
    elements_text: str                      # AI 可读的元素列表文本
    screenshot: "Image.Image | None"        # Tier 3 时包含截图
    window_info: "WindowInfo"               # 活动窗口信息
    ui_elements: list["UIElement"] | None   # Tier 1 时包含结构化元素
    ocr_results: list["OcrResult"] | None   # Tier 2 时包含 OCR 结果


class WindowPerceiver:
    """三级感知策略编排器，协调 UIA/OCR/AI 视觉。"""

    def __init__(
        self,
        window_manager: "WindowManager",
        uia_scanner: "UIAutomationScanner",
        screen_capture: "ScreenCapture",
        ocr_engine: "OcrEngine",
        ai_analyzer: "AIVisualAnalyzer",
    ) -> None: ...

    async def inspect(
        self,
        target_window: str | None = None,
        force_tier: int | None = None,
    ) -> PerceptionResult:
        """执行三级感知流程。
        
        Args:
            target_window: 目标窗口标题/进程名，None 表示当前活动窗口
            force_tier: 强制使用指定 Tier (调试用)
            
        流程:
        1. 激活/获取目标窗口信息
        2. Tier 1: UIA 扫描 → 若获取到足够元素则返回
        3. Tier 2: OCR 扫描 → 序列化文本返回
        4. (Tier 3 由 AI 在 ReAct 循环中按需触发)
        """
        ...

    async def locate_and_convert(
        self,
        ratio_point: "RatioPoint",
        window_info: "WindowInfo",
    ) -> "ScreenPoint":
        """将 AI 返回的比例坐标转换为屏幕绝对坐标。"""
        ...
```

### 物理交互

```python
# server/lumina/vision/interaction.py

class PhysicalInteraction:
    """物理鼠标/键盘操作封装。所有坐标为屏幕绝对像素。"""

    async def click(self, x: int, y: int) -> None: ...
    async def double_click(self, x: int, y: int) -> None: ...
    async def right_click(self, x: int, y: int) -> None: ...
    async def drag(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None: ...
    async def type_text(self, text: str) -> None: ...
    async def hotkey(self, *keys: str) -> None: ...
    async def move_mouse(self, x: int, y: int, duration: float = 0.0) -> None: ...
```

### 工具定义（注册到 ToolRegistry）

```python
# server/lumina/tools/vision_tools.py


class InspectWindowTool(BaseTool):
    name = "inspect_window"
    description = (
        "感知目标应用窗口的 UI 元素信息。"
        "自动激活窗口并扫描其 UI 控件和文字，返回可交互元素列表及其位置(比例坐标)。"
        "若不指定窗口则感知当前活动窗口。"
        "返回的信息包含元素名称、类型和比例坐标，可用于后续的 click_at 等操作。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "window": {
                "type": "string",
                "description": "目标窗口的标题关键字或进程名，不指定则使用当前活动窗口"
            },
            "force_tier": {
                "type": "integer",
                "enum": [1, 2, 3],
                "description": "强制使用指定识别层级: 1=UIA, 2=OCR, 3=AI视觉。通常无需指定。"
            }
        },
        "required": []
    }
    risk_level = RiskLevel.LOW

    async def execute(self, window: str | None = None, force_tier: int | None = None) -> str:
        """返回 AI 可读的元素列表文本。"""
        ...


class VisualLocateTool(BaseTool):
    name = "visual_locate"
    description = (
        "当 inspect_window 返回的文字信息不足以定位目标时使用。"
        "将活动窗口截图发送给 AI 进行视觉分析，定位图标、无标签按钮等非文字元素。"
        "注意: 此工具需要当前模型支持图像理解。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "要定位的元素描述，如 '设置齿轮图标'、'红色关闭按钮'"
            },
            "window": {
                "type": "string",
                "description": "目标窗口，不指定则使用当前活动窗口"
            }
        },
        "required": ["description"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, description: str, window: str | None = None) -> str: ...


class ClickAtTool(BaseTool):
    name = "click_at"
    description = (
        "在活动窗口中点击指定比例位置。"
        "桌宠会跑到目标位置，播放点击动画，然后触发真实的鼠标点击。"
        "坐标为相对活动窗口的比例值 (0.0~1.0)。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "rx": {"type": "number", "description": "水平比例坐标 (0.0=最左, 1.0=最右)"},
            "ry": {"type": "number", "description": "垂直比例坐标 (0.0=最上, 1.0=最下)"},
            "click_type": {
                "type": "string",
                "enum": ["single", "double", "right"],
                "description": "点击类型，默认 single"
            }
        },
        "required": ["rx", "ry"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, rx: float, ry: float, click_type: str = "single") -> str:
        """换算比例坐标为屏幕像素 → 驱动桌宠 → 物理点击。"""
        ...


class TypeTextTool(BaseTool):
    name = "type_text"
    description = "在当前焦点位置输入文字。通常需先用 click_at 点击目标输入框。"
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "要输入的文字"}
        },
        "required": ["text"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, text: str) -> str: ...


class HotkeyTool(BaseTool):
    name = "hotkey"
    description = "执行键盘快捷键组合，如 Ctrl+C、Alt+F4 等。"
    parameters = {
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {"type": "string"},
                "description": "按键序列，如 ['ctrl', 'c']"
            }
        },
        "required": ["keys"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, keys: list[str]) -> str: ...
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

1. **安装依赖**: 添加 `mss`, `paddleocr`, `paddlepaddle`, `pyautogui`, `Pillow`, `uiautomation`, `pywin32` 到 `pyproject.toml`。
2. **实现活动窗口管理** (`server/lumina/vision/window_info.py`): 封装 `win32gui` 实现窗口查找、激活、矩形获取。
3. **实现比例坐标转换** (`server/lumina/vision/coordinates.py`): `RatioPoint`, `ScreenPoint`, `CoordinateConverter`。
4. **实现 Tier 1 — UIA 扫描** (`server/lumina/vision/ui_automation.py`): 使用 `uiautomation` 库扫描窗口元素树，序列化为 AI 可读文本。
5. **实现 Tier 2 — 屏幕截图** (`server/lumina/vision/capture.py`): 基于 `mss` 的活动窗口区域截图 + 缩放。
6. **实现 Tier 2 — OCR 引擎** (`server/lumina/vision/ocr.py`): 封装 PaddleOCR，延迟加载，结果含比例坐标。
7. **实现 Tier 3 — AI 视觉分析** (`server/lumina/vision/ai_visual.py`): 多模态请求封装，检查模型能力。
8. **实现感知编排器** (`server/lumina/vision/perceiver.py`): `WindowPerceiver` 协调三级策略。
9. **实现物理交互** (`server/lumina/vision/interaction.py`): 封装 `pyautogui` 的鼠标/键盘操作。
10. **实现工具集** (`server/lumina/tools/vision_tools.py`): `InspectWindowTool`, `VisualLocateTool`, `ClickAtTool`, `TypeTextTool`, `HotkeyTool`。
11. **扩展 WebSocket 协议**: 在 `protocol.py` 中添加 `pet_event` 消息类型。
12. **扩展 Godot 桌宠**: 在 `pet_controller.gd` 中添加 `perform_click_at()` 方法和 CLICKING 状态。在关键帧通过 WebSocket 发送 `click_ready` 事件。
13. **实现 ClickAtTool 的协调逻辑**: 比例坐标换算 → 发送 `move_to` → 等待 `click_ready` → 执行 `pyautogui.click` → 状态恢复。
14. **注册工具到 Agent**: 在启动时将所有视觉工具注册到 `ToolRegistry`。
15. **编写测试** (`server/tests/test_vision.py`):
    - 测试 `CoordinateConverter` 的双向换算精度
    - 测试 `UIAutomationScanner` 对记事本等标准应用的元素扫描
    - 测试 `OcrEngine` 对中英文的识别和比例坐标计算
    - 测试 `WindowPerceiver` 的三级降级流程
16. **端到端验证**: 发送 "帮我在记事本中输入 Hello" → Agent 调用 `inspect_window("记事本")` → 获得元素列表 (UIA Tier 1) → 调用 `click_at(0.50, 0.52)` 点击编辑区 → 调用 `type_text("Hello")`。

## §6 Acceptance Criteria

**⚠ MANDATORY: Every item must be verified and checked `[x]` before proceeding to §7.**

### Functional Verification
- [ ] `WindowManager.get_foreground_window()` 返回正确的窗口标题、进程名和矩形
- [ ] `WindowManager.activate_window()` 能将后台窗口切到前台
- [ ] `CoordinateConverter.ratio_to_screen()` 换算正确 — 测试边界值 (0.0, 0.0) 和 (1.0, 1.0)
- [ ] `CoordinateConverter.screen_to_ratio()` 反向换算与正向一致 (往返精度测试)
- [ ] `UIAutomationScanner.scan_window()` 对记事本返回 Button, Edit 等标准元素
- [ ] `UIAutomationScanner.serialize_for_llm()` 输出包含元素名称、类型和比例坐标
- [ ] `WindowPerceiver.inspect()` Tier 1 成功时不触发 Tier 2/3
- [ ] `WindowPerceiver.inspect()` Tier 1 失败时自动降级到 Tier 2 (OCR)
- [ ] `OcrEngine.recognize()` 能识别活动窗口区域的中英文文字
- [ ] OCR 结果的 `ratio_center` 与实际位置偏差 < 5%
- [ ] `ClickAtTool` 完整链路: 比例坐标换算 → 桌宠移动 → 到达 → 点击动画 → 物理点击 → idle
- [ ] `VisualLocateTool` 在 AI 不支持图像时返回友好提示而非崩溃
- [ ] 桌宠在 `inspect_window` 执行期间切换到 OBSERVING 状态

### Test Verification
- [ ] 单元测试 `pytest server/tests/test_vision.py` 通过，0 failures
- [ ] 测试覆盖: `CoordinateConverter`, `UIAutomationScanner`, `OcrEngine`, `WindowPerceiver` 降级逻辑

### Integration Verification
- [ ] 端到端: Godot 发送 "帮我在记事本中输入Hello" → Agent 调用 `inspect_window` → `click_at` → `type_text` → 记事本中出现 "Hello"

### Code Quality
- [ ] `server/lumina/vision/` 下所有文件无 linter 错误
- [ ] `server/lumina/tools/vision_tools.py` 无 linter 错误

## §7 State Teardown Checklist

**⚠ MANDATORY: Every item is a concrete action. Complete each one and check `[x]`.**

- [ ] **§3/§4 Updated**: 若实现中设计/接口有变，更新本文档 §3 和 §4 使其与最终代码一致
- [ ] **changelog.md**: 追加本阶段条目 (Delivered/Decisions/Deferred) → `../changelog.md`
- [ ] **api_registry/tool_system.md**: 更新视觉工具和支撑模块条目 → `../api_registry/tool_system.md`
- [ ] **api_registry/websocket_protocol.md**: 新增 `pet_event` 消息类型 → `../api_registry/websocket_protocol.md`
- [ ] **api_registry/godot_ui.md**: 新增 CLICKING/OBSERVING 状态和 `click_ready`/`action_completed` 信号 → `../api_registry/godot_ui.md`
- [ ] **master_overview.md**: 将 Phase 05 状态改为 `[x] Done` → `../master_overview.md`
- [ ] **§2 checkboxes**: 将本文档 §2 中所有 Reference Materials 和 Source files 标记为 `[x]`
