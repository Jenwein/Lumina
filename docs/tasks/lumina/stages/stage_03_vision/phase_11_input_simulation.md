# Phase 11: 输入模拟工具

## §1 Goal
实现鼠标点击/拖拽、键盘输入、组合键的跨平台模拟，注册为 Agent 工具。

## §2 Dependencies
- **Prerequisite phases**: Phase 06
- **Source files to read**: `server/src/lumina/agent/tool_registry.py`, `server/src/lumina/tools/`

## §3 Design & Constraints
- **Architecture principles**:
  - 使用 `pyautogui` 实现跨平台鼠标和键盘模拟
  - 鼠标功能：click, double_click, right_click, drag, move_to（支持 duration 参数实现平滑移动）
  - 键盘功能：type_text, hotkey, key_down, key_up
  - 所有坐标为绝对屏幕坐标
  - 所有函数注册为 Agent 工具，通过 ToolRegistry 管理
  - 异步包装：通过 `run_in_executor` 将同步 pyautogui 调用包装为 async 接口
- **Boundary conditions**:
  - `pyautogui.FAILSAFE` 始终启用（将鼠标移至屏幕角落可中止操作）
  - 鼠标移动最小 duration 可配置，防止瞬移导致误操作
  - ToolResult 统一返回操作结果（成功/失败 + 描述信息）
  - 坐标超出屏幕范围时应返回错误而非抛异常
- **Out of scope**: OCR 引导点击（Phase 12）、多显示器坐标转换（Phase 13）

## §4 Interface Contract

```python
# server/src/lumina/tools/input_tools.py
from lumina.agent.tool_registry import ToolResult

async def mouse_click(x: int, y: int, button: str = "left", clicks: int = 1) -> ToolResult:
    """在指定坐标执行鼠标点击。button: 'left' | 'right' | 'middle'"""
    ...

async def mouse_drag(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5) -> ToolResult:
    """从起点拖拽到终点，duration 控制拖拽速度。"""
    ...

async def mouse_move(x: int, y: int, duration: float = 0.3) -> ToolResult:
    """将鼠标移动到指定坐标，duration 控制移动速度。"""
    ...

async def keyboard_type(text: str, interval: float = 0.05) -> ToolResult:
    """逐字符输入文本，interval 为字符间隔秒数。"""
    ...

async def keyboard_hotkey(*keys: str) -> ToolResult:
    """执行组合键，如 keyboard_hotkey('ctrl', 'c')。"""
    ...

async def keyboard_press(key: str) -> ToolResult:
    """按下并释放单个按键。"""
    ...
```

## §5 Implementation Steps
1. 在 `server/pyproject.toml` 中添加 `pyautogui` 依赖
2. 创建 `server/src/lumina/tools/input_tools.py` — 实现鼠标和键盘模拟函数
3. 在 `server/src/lumina/tools/registry.py` 中注册所有输入工具，生成 JSON Schema
4. 创建 `server/tests/test_input_tools.py` — 使用 pyautogui 测试模式 (PAUSE=0) 验证

## §6 Acceptance Criteria
- [ ] `mouse_click` 在指定坐标发送点击事件
- [ ] `mouse_drag` 在两点间执行平滑拖拽
- [ ] `keyboard_type` 正确输入文本内容
- [ ] `keyboard_hotkey` 发送组合键（如 Ctrl+C）
- [ ] 所有工具已注册到 ToolRegistry 且具有正确的 JSON Schema 描述
- [ ] `pyautogui.FAILSAFE` 已启用
- [ ] 测试通过（使用 pyautogui 内置测试模式）

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
