# Phase 12: 视觉交互全链路

## §1 Goal
串联截屏→OCR/视觉分析→坐标定位→桌宠移动→点击动画→物理点击的完整工作流。

## §2 Dependencies
- **Prerequisite phases**: Phase 04, Phase 10, Phase 11
- **Source files to read**: `server/src/lumina/vision/`, `server/src/lumina/tools/input_tools.py`, `server/src/lumina/ws/`

## §3 Design & Constraints
- **Architecture principles**:
  - 编排器模式（Orchestrator）：协调视觉交互全流程的各个子系统
  - 完整流程：截取屏幕 → 分析（OCR 或 LLM Vision）→ 定位目标元素 → 通过 WebSocket 发送移动指令给桌宠 → 等待桌宠到达事件 → 触发点击动画 → 执行物理点击 → 可选结果验证
  - 注册为高级 Agent 工具：`click_on_element`
  - 重试逻辑：元素未找到时重新截屏并重试，最多 3 次
  - 超时机制：桌宠移动 + 动画等待可配置最大超时
- **Boundary conditions**:
  - 桌宠必须先"走到"目标位置再执行物理点击，确保视觉一致性
  - 需等待 Godot 端返回 `pet_arrived` 事件后才继续后续步骤
  - use_ocr 参数控制分析策略：True 优先 OCR，False 使用 LLM Vision
  - 物理点击前桌宠需播放点击动画，动画完成后再触发 pyautogui 点击
- **Out of scope**: 多显示器目标定位（Phase 13）、安全确认机制（Phase 16）

## §4 Interface Contract

```python
# server/src/lumina/vision/interaction_chain.py
from pydantic import BaseModel
from lumina.vision.capture import ScreenCapture
from lumina.vision.ocr import OCREngine
from lumina.vision.analyzer import VisionAnalyzer, ElementLocation

class ClickResult(BaseModel):
    success: bool
    target_description: str
    click_position: tuple[int, int]
    pet_moved: bool
    error: str | None = None

class VisualInteractionChain:
    def __init__(
        self,
        capture: ScreenCapture,
        ocr: OCREngine,
        analyzer: VisionAnalyzer,
        input_sim: "InputSimulator",
        ws_manager: "ConnectionManager",
    ):
        """初始化视觉交互链，注入所有依赖。"""
        ...

    async def click_element(self, description: str, use_ocr: bool = True) -> ClickResult:
        """
        完整链路：截屏 → 定位元素 → 移动桌宠 → 播放动画 → 物理点击。
        支持最多 3 次重试。
        """
        ...

    async def find_and_report(self, query: str) -> list[ElementLocation]:
        """截屏并分析，返回匹配的元素位置列表（不执行点击）。"""
        ...
```

```gdscript
# client/scripts/pet/pet_click_animation.gd — WebSocket 命令处理
# 收到 {"action": "pet_click", "payload": {"x": int, "y": int}} 时：
# 1. 桌宠移动到 (x, y)
# 2. 播放点击动画
# 3. 动画完成后发送 {"action": "pet_click_done", "payload": {"x": int, "y": int}}
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/vision/interaction_chain.py` — VisualInteractionChain 编排器
2. 实现完整管道：capture → analyze → locate → move pet → animate → click → verify
3. 在 WebSocket 协议中添加 `pet_click` 命令，触发桌宠移动+点击动画
4. 创建 `client/scripts/pet/pet_click_animation.gd` — 桌宠移动到目标并播放点击动画
5. 将 `click_on_element` 注册为 Agent 工具
6. 创建 `server/tests/test_interaction_chain.py` — 使用 mock 依赖的集成测试

## §6 Acceptance Criteria
- [ ] 完整链路可执行：屏幕截取 → 元素定位 → 桌宠移动 → 物理点击完成
- [ ] 桌宠在物理点击前视觉上"走到"目标位置
- [ ] 重试逻辑生效：首次未找到元素时自动重新截屏并重试
- [ ] ClickResult 正确报告成功/失败及详细信息
- [ ] 超时机制正常工作，超时后返回失败结果而非无限等待
- [ ] 集成测试（mock 依赖）全部通过

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
