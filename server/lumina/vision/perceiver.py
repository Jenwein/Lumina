from dataclasses import dataclass
from PIL import Image
from typing import List, Optional, Tuple, TYPE_CHECKING
from .window_info import WindowManager, WindowInfo, WindowRect
from .ui_automation import UIAutomationScanner, UIElement
from .capture import ScreenCapture
from .ocr import OcrEngine, OcrResult
from .ai_visual import AIVisualAnalyzer
from .coordinates import RatioPoint, ScreenPoint, CoordinateConverter

if TYPE_CHECKING:
    from ..agent.llm_client import LLMClient


@dataclass
class PerceptionResult:
    """三级感知的统一输出。"""
    tier_used: int                          # 1, 2, 3
    elements_text: str                      # AI 可读的元素列表文本
    screenshot: Optional[Image.Image]       # Tier 3 时包含截图
    window_info: WindowInfo                 # 活动窗口信息
    ui_elements: Optional[List[UIElement]]   # Tier 1 时包含结构化元素
    ocr_results: Optional[List[OcrResult]]   # Tier 2 时包含 OCR 结果


class WindowPerceiver:
    """三级感知策略编排器，协调 UIA/OCR/AI 视觉。"""

    def __init__(
        self,
        window_manager: WindowManager,
        uia_scanner: UIAutomationScanner,
        screen_capture: ScreenCapture,
        ocr_engine: OcrEngine,
        ai_analyzer: AIVisualAnalyzer,
    ) -> None:
        self.window_manager = window_manager
        self.uia_scanner = uia_scanner
        self.screen_capture = screen_capture
        self.ocr_engine = ocr_engine
        self.ai_analyzer = ai_analyzer

    async def inspect(
        self,
        target_window: Optional[str] = None,
        force_tier: Optional[int] = None,
    ) -> Optional[PerceptionResult]:
        """执行三级感知流程。"""
        # 1. 查找/获取目标窗口
        window_info = None
        if target_window:
            window_info = self.window_manager.find_window(title_query=target_window)
            if not window_info:
                window_info = self.window_manager.find_window(process_query=target_window)
        
        if not window_info:
            window_info = self.window_manager.get_foreground_window()
        
        if not window_info:
            return None

        # 2. 激活窗口
        self.window_manager.activate_window(window_info.hwnd)
        # 激活后窗口位置可能变化，重新获取
        window_info.rect = self.window_manager.get_window_rect(window_info.hwnd)

        # Tier 1: UIA
        if force_tier is None or force_tier == 1:
            ui_elements = self.uia_scanner.scan_window(window_info.hwnd)
            if ui_elements and (force_tier == 1 or len(ui_elements) > 2):
                text = self.uia_scanner.serialize_for_llm(ui_elements, window_info.rect)
                return PerceptionResult(
                    tier_used=1,
                    elements_text=text,
                    screenshot=None,
                    window_info=window_info,
                    ui_elements=ui_elements,
                    ocr_results=None
                )

        # Tier 2: OCR
        if force_tier is None or force_tier <= 2:
            img = self.screen_capture.capture_window(window_info.rect)
            ocr_results = self.ocr_engine.recognize(img)
            if ocr_results and (force_tier == 2 or len(ocr_results) > 0):
                text = self.ocr_engine.serialize_for_llm(ocr_results, window_info.title)
                return PerceptionResult(
                    tier_used=2,
                    elements_text=text,
                    screenshot=img, # 即使是 Tier 2 也保存截图供后续可能用
                    window_info=window_info,
                    ui_elements=None,
                    ocr_results=ocr_results
                )

        # Tier 3 (通常不由 inspect 自动触发，除非 force_tier=3)
        if force_tier == 3:
            img = self.screen_capture.capture_window_for_ai(window_info.rect)
            return PerceptionResult(
                tier_used=3,
                elements_text="[Tier 3] 请使用 visual_locate 获取特定元素坐标。",
                screenshot=img,
                window_info=window_info,
                ui_elements=None,
                ocr_results=None
            )

        return None

    def locate_and_convert(
        self,
        ratio_point: RatioPoint,
        window_rect: WindowRect,
    ) -> ScreenPoint:
        """将 AI 返回的比例坐标转换为屏幕绝对坐标。"""
        return CoordinateConverter.ratio_to_screen(ratio_point, window_rect)
