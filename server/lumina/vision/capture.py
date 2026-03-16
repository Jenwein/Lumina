import mss
import mss.tools
from PIL import Image
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .window_info import WindowRect


class ScreenCapture:
    """基于 mss 的屏幕截图，支持活动窗口区域截取。"""

    def __init__(self):
        self.sct = mss.mss()

    def capture_window(self, window_rect: "WindowRect", max_long_edge: int = 1280) -> Image.Image:
        """截取活动窗口区域并按比例缩放。"""
        # (left, top, right, bottom)
        monitor = {
            "left": window_rect.x,
            "top": window_rect.y,
            "width": window_rect.width,
            "height": window_rect.height
        }
        
        # 截图
        sct_img = self.sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # 缩放
        if max_long_edge > 0:
            img = self._resize_if_needed(img, max_long_edge)
            
        return img

    def capture_window_for_ai(self, window_rect: "WindowRect", max_long_edge: int = 768) -> Image.Image:
        """截取活动窗口区域，缩放到适合发送给 AI 的尺寸。"""
        return self.capture_window(window_rect, max_long_edge)

    def capture_full(self, monitor_index: int = 1) -> Image.Image:
        """截取指定显示器全屏。"""
        if monitor_index >= len(self.sct.monitors):
            monitor_index = 0
            
        monitor = self.sct.monitors[monitor_index]
        sct_img = self.sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def _resize_if_needed(self, img: Image.Image, max_long_edge: int) -> Image.Image:
        w, h = img.size
        if w <= max_long_edge and h <= max_long_edge:
            return img
            
        if w > h:
            new_w = max_long_edge
            new_h = int(h * (max_long_edge / w))
        else:
            new_h = max_long_edge
            new_w = int(w * (max_long_edge / h))
            
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
