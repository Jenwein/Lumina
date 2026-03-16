import win32gui
import win32process
import psutil
from dataclasses import dataclass
from typing import Optional


@dataclass
class WindowRect:
    x: int
    y: int
    width: int
    height: int


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    process_name: str
    rect: WindowRect
    is_foreground: bool


class WindowManager:
    """活动窗口管理：查找、激活、获取信息。"""

    def get_foreground_window(self) -> Optional[WindowInfo]:
        """获取当前前台窗口信息。"""
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        return self._get_window_info(hwnd)

    def find_window(self, title_query: Optional[str] = None, process_query: Optional[str] = None) -> Optional[WindowInfo]:
        """按标题关键字或进程名查找窗口。"""
        found_hwnd = []

        def enum_windows_callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return

            # 按标题匹配
            if title_query and title_query.lower() in title.lower():
                found_hwnd.append(hwnd)
                return

            # 按进程名匹配
            if process_query:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    proc = psutil.Process(pid)
                    if process_query.lower() in proc.name().lower():
                        found_hwnd.append(hwnd)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        win32gui.EnumWindows(enum_windows_callback, None)
        
        if not found_hwnd:
            return None
        
        # 返回第一个匹配的
        return self._get_window_info(found_hwnd[0])

    def activate_window(self, hwnd: int) -> bool:
        """将指定窗口设为前台，包含绕过 Windows 限制的逻辑。"""
        import win32con
        import win32api
        try:
            # 如果窗口最小化了，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

            # 模拟 Alt 键以允许抢占焦点 (Windows 限制只有当前活跃进程能设置前台)
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32gui.SetForegroundWindow(hwnd)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            from logging import getLogger
            getLogger("lumina").warning(f"Failed to activate window {hwnd}: {e}")
            return False

    def get_window_rect(self, hwnd: int) -> WindowRect:
        """获取窗口矩形。"""
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        return WindowRect(
            x=left,
            y=top,
            width=right - left,
            height=bottom - top
        )

    def _get_window_info(self, hwnd: int) -> WindowInfo:
        title = win32gui.GetWindowText(hwnd)
        rect = self.get_window_rect(hwnd)
        
        process_name = "unknown"
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            process_name = proc.name()
        except Exception:
            pass

        is_foreground = (hwnd == win32gui.GetForegroundWindow())
        
        return WindowInfo(
            hwnd=hwnd,
            title=title,
            process_name=process_name,
            rect=rect,
            is_foreground=is_foreground
        )
