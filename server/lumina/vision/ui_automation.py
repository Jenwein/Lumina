import uiautomation as auto
from dataclasses import dataclass
from typing import List, Optional, Tuple, TYPE_CHECKING
import platform

if TYPE_CHECKING:
    from .window_info import WindowRect


@dataclass
class UIElement:
    name: str                       # 元素显示名称
    control_type: str               # Button, Edit, MenuItem, CheckBox, etc.
    automation_id: str              # 自动化ID
    bounding_rect: Tuple[int, int, int, int]  # (x, y, width, height) 屏幕像素
    is_enabled: bool                # 是否可交互
    value: Optional[str] = None     # 当前值 (输入框的文字等)
    children_count: int = 0


class UIAutomationScanner:
    """通过 Windows UI Automation 扫描窗口元素树。"""

    def scan_window(self, hwnd: int, max_depth: int = 5) -> List[UIElement]:
        """扫描指定窗口的 UI 元素树，返回可交互元素列表。"""
        if not self.is_available():
            return []

        window_element = auto.ControlFromHandle(hwnd)
        if not window_element:
            return []

        elements = []
        self._traverse_elements(window_element, 0, max_depth, elements)
        return elements

    def _traverse_elements(self, element, current_depth: int, max_depth: int, elements: List[UIElement]):
        if current_depth > max_depth:
            return

        # 检查是否为可交互元素或重要容器
        # 我们主要关注可交互元素
        has_name = element.Name != ""
        is_interactive = element.IsEnabled and (
            element.ControlType in [
                auto.ControlType.ButtonControl,
                auto.ControlType.EditControl,
                auto.ControlType.MenuItemControl,
                auto.ControlType.CheckBoxControl,
                auto.ControlType.RadioButtonControl,
                auto.ControlType.ComboBoxControl,
                auto.ControlType.HyperlinkControl,
                auto.ControlType.ListItemControl,
                auto.ControlType.TreeItemControl,
                auto.ControlType.TabItemControl,
            ]
        )

        if has_name:
            rect = element.BoundingRectangle
            # (left, top, right, bottom) -> (x, y, width, height)
            if rect.width() > 0 and rect.height() > 0:
                bounding_rect = (rect.left, rect.top, rect.width(), rect.height())
                
                # 尝试获取 Value
                val = None
                try:
                    if hasattr(element, "GetValuePattern"):
                        pattern = element.GetValuePattern()
                        if pattern:
                            val = pattern.Value
                except Exception:
                    pass

                elements.append(UIElement(
                    name=element.Name,
                    control_type=element.ControlTypeName,
                    automation_id=element.AutomationId,
                    bounding_rect=bounding_rect,
                    is_enabled=element.IsEnabled,
                    value=val,
                    children_count=0 
                ))

        # 递归子元素
        for child in element.GetChildren():
            self._traverse_elements(child, current_depth + 1, max_depth, elements)

    def serialize_for_llm(self, elements: List[UIElement], window_rect: "WindowRect") -> str:
        """将元素列表序列化为 AI 可读的纯文本。"""
        if not elements:
            return "未发现可交互的 UI 元素。"

        lines = [f"[窗口元素列表 — 共有 {len(elements)} 个元素]"]
        for i, el in enumerate(elements, 1):
            # 转换为比例坐标
            rx = (el.bounding_rect[0] + el.bounding_rect[2] / 2 - window_rect.x) / window_rect.width
            ry = (el.bounding_rect[1] + el.bounding_rect[3] / 2 - window_rect.y) / window_rect.height
            
            # 限制范围
            rx = max(0.0, min(1.0, rx))
            ry = max(0.0, min(1.0, ry))

            status = "可用" if el.is_enabled else "禁用"
            val_str = f" 值:\"{el.value}\"" if el.value else ""
            lines.append(f"{i}. [{el.control_type}] \"{el.name}\" 位置:({rx:.2f}, {ry:.2f}) {status}{val_str}")
        
        return "\n".join(lines)

    @staticmethod
    def is_available() -> bool:
        """检查 UIA 是否可用 (仅 Windows)。"""
        return platform.system() == "Windows"
