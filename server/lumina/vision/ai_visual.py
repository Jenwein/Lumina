import base64
from io import BytesIO
from PIL import Image
from typing import Optional, TYPE_CHECKING
from .coordinates import RatioPoint

if TYPE_CHECKING:
    from ..agent.llm_client import LLMClient


class AIVisualAnalyzer:
    """将窗口截图发送给 AI 进行视觉定位的兜底方案。"""

    def __init__(self, llm_client: "LLMClient") -> None:
        self.llm_client = llm_client

    async def locate_element(
        self,
        image: Image.Image,
        description: str,
        ocr_context: str = "",
    ) -> Optional[RatioPoint]:
        """请求 AI 在截图中定位指定元素，返回比例坐标。"""
        if not self.check_multimodal_support():
            return None

        # 将图片转为 Base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        prompt = f"""你是一个视觉助手，需要在一张软件窗口截图中定位特定的 UI 元素。

目标元素描述: "{description}"

上下文 (OCR 识别到的文字):
{ocr_context}

请根据图片和文字上下文，找到 "{description}"。
返回其在图片中的中心点比例坐标 (rx, ry)，rx 和 ry 均在 0.0 到 1.0 之间。
仅返回坐标，格式为 "(rx, ry)"，例如 "(0.52, 0.45)"。
如果你无法确定位置，请返回 "NONE"。"""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_str}"}
                    },
                ],
            }
        ]

        try:
            response = await self.llm_client.chat_completion(messages)
            content = response.strip()
            
            if content == "NONE":
                return None
            
            # 解析 (rx, ry)
            content = content.replace("(", "").replace(")", "").replace(" ", "")
            parts = content.split(",")
            if len(parts) == 2:
                return RatioPoint(rx=float(parts[0]), ry=float(parts[1]))
        except Exception:
            pass

        return None

    def check_multimodal_support(self) -> bool:
        """检查当前 LLM 是否支持图像输入。"""
        # glm-4-flash 实际上不支持视觉（除非是特定版本，但通常 flash 是文本）
        # 这里我们可以硬编码或者从配置中读取
        # 暂时简单返回 True，若调用失败则回退
        return True
