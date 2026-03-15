from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
from PIL import Image
from .coordinates import RatioPoint


@dataclass
class OcrResult:
    text: str
    bbox_x: int             # 在截图中的像素位置
    bbox_y: int
    bbox_width: int
    bbox_height: int
    confidence: float
    ratio_center: RatioPoint   # 相对窗口的比例坐标(中心点)


class OcrEngine:
    """EasyOCR 封装，延迟加载模型。"""

    def __init__(self, lang: str = "ch") -> None:
        self.lang = lang
        self._reader = None  # 首次调用时初始化

    def _ensure_reader(self):
        if self._reader is None:
            import easyocr
            # ['ch_sim', 'en'] 覆盖中英文
            self._reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        return self._reader

    def recognize(self, image: Image.Image) -> List[OcrResult]:
        """对图像执行 OCR，返回结果列表(含比例坐标)。"""
        reader = self._ensure_reader()
        
        # PIL Image -> numpy array (RGB)
        img_array = np.array(image)
        
        # EasyOCR 接收 ndarray
        results = reader.readtext(img_array)
        
        if not results:
            return []

        ocr_results = []
        img_w, img_h = image.size

        for (bbox, text, confidence) in results:
            # bbox: [[x0, y0], [x1, y1], [x2, y2], [x3, y3]]
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            
            w = max_x - min_x
            h = max_y - min_y
            
            center_x = min_x + w / 2
            center_y = min_y + h / 2
            
            ocr_results.append(OcrResult(
                text=text,
                bbox_x=int(min_x),
                bbox_y=int(min_y),
                bbox_width=int(w),
                bbox_height=int(h),
                confidence=float(confidence),
                ratio_center=RatioPoint(
                    rx=center_x / img_w,
                    ry=center_y / img_h
                )
            ))
            
        return ocr_results

    def serialize_for_llm(self, results: List[OcrResult], window_title: str) -> str:
        """将 OCR 结果序列化为 AI 可读的纯文本。"""
        if not results:
            return f"[活动窗口 OCR — {window_title}] 未识别到文字。"

        lines = [f"[活动窗口 OCR — {window_title} (共有 {len(results)} 条文字)]"]
        for i, res in enumerate(results, 1):
            lines.append(f"{i}. \"{res.text}\" 位置:({res.ratio_center.rx:.2f}, {res.ratio_center.ry:.2f}) 置信度:{res.confidence:.2f}")
        
        return "\n".join(lines)
