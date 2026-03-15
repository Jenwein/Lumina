from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .window_info import WindowRect


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
        if window.width == 0 or window.height == 0:
            return RatioPoint(0.0, 0.0)
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
        if image_width == 0 or image_height == 0:
            return RatioPoint(0.0, 0.0)
        return RatioPoint(
            rx=center_x / image_width,
            ry=center_y / image_height,
        )
