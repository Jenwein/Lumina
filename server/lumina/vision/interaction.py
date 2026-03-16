import pyautogui
import asyncio


class PhysicalInteraction:
    """物理鼠标/键盘操作封装。所有坐标为屏幕绝对像素。"""

    def __init__(self):
        # 禁用故障安全以避免非预期中断，但在生产中应谨慎
        pyautogui.FAILSAFE = True

    async def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> None:
        """执行鼠标点击。"""
        # pyautogui 操作通常是阻塞的，但在单独的执行步骤中运行
        pyautogui.click(x, y, button=button, clicks=clicks)

    async def double_click(self, x: int, y: int) -> None:
        """执行鼠标双击。"""
        pyautogui.doubleClick(x, y)

    async def right_click(self, x: int, y: int) -> None:
        """执行鼠标右键。"""
        pyautogui.rightClick(x, y)

    async def drag(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        """执行拖拽。"""
        pyautogui.moveTo(from_x, from_y)
        pyautogui.dragTo(to_x, to_y, duration=0.5)

    async def type_text(self, text: str) -> None:
        """输入文本。"""
        pyautogui.write(text, interval=0.01)

    async def hotkey(self, *keys: str) -> None:
        """按快捷键。"""
        pyautogui.hotkey(*keys)

    async def move_mouse(self, x: int, y: int, duration: float = 0.0) -> None:
        """移动鼠标。"""
        pyautogui.moveTo(x, y, duration=duration)
