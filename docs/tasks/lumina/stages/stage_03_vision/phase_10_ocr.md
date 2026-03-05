# Phase 10: OCR 与视觉分析

## §1 Goal
集成 PaddleOCR 实现文字识别和定位，结合 LLM 多模态视觉实现语义级元素检测。

## §2 Dependencies
- **Prerequisite phases**: Phase 09
- **Source files to read**: `server/src/lumina/vision/capture.py`, `server/src/lumina/llm/client.py`

## §3 Design & Constraints
- **Architecture principles**:
  - PaddleOCR：文字识别，返回带边界框和置信度的结果
  - LLM Vision：将截图编码为 base64 发送至多模态 LLM，获取语义级理解
  - 双层策略：OCR 处理文字元素，LLM Vision 处理图标/图片/复杂 UI
  - 结果归一化为屏幕坐标（与 ScreenCapture 坐标系一致）
  - PaddleOCR 模型延迟加载（首次加载较重），跨调用缓存模型实例
- **Boundary conditions**:
  - OCR 默认语言为中文 (`ch`)，可通过构造参数切换
  - LLM Vision 依赖外部 API 可用性，需处理超时和错误
  - bbox 格式统一为 (x, y, w, h) 屏幕坐标
  - find_text 使用子串匹配过滤 OCR 结果
- **Out of scope**: 实时连续 OCR、训练自定义模型

## §4 Interface Contract

```python
# server/src/lumina/vision/ocr.py
from pydantic import BaseModel
from PIL import Image

class OCRResult(BaseModel):
    text: str
    bbox: tuple[int, int, int, int]  # x, y, w, h in screen coords
    confidence: float

class OCREngine:
    def __init__(self, lang: str = "ch"):
        """初始化 OCR 引擎，模型延迟加载。"""
        ...

    async def recognize(self, image: Image.Image) -> list[OCRResult]:
        """对整张图片执行 OCR，返回所有识别结果。"""
        ...

    async def find_text(self, image: Image.Image, target: str) -> list[OCRResult]:
        """执行 OCR 后按目标字符串过滤，返回匹配结果。"""
        ...
```

```python
# server/src/lumina/vision/analyzer.py
from pydantic import BaseModel
from PIL import Image

class ElementLocation(BaseModel):
    description: str
    bbox: tuple[int, int, int, int]  # x, y, w, h in screen coords
    confidence: float

class VisionAnalyzer:
    def __init__(self, llm_client: "LLMClient"):
        """初始化视觉分析器，绑定 LLM 客户端。"""
        ...

    async def analyze_screen(self, image: Image.Image, query: str) -> str:
        """将截图发送至 LLM 多模态接口，返回自然语言描述。"""
        ...

    async def find_element(self, image: Image.Image, description: str) -> list[ElementLocation]:
        """通过 LLM 视觉能力定位指定 UI 元素，返回位置列表。"""
        ...
```

## §5 Implementation Steps
1. 在 `server/pyproject.toml` 中添加 `paddleocr` 和 `paddlepaddle` 依赖
2. 创建 `server/src/lumina/vision/ocr.py` — OCREngine 封装 PaddleOCR，含 lazy 加载和 async 包装
3. 创建 `server/src/lumina/vision/analyzer.py` — VisionAnalyzer 封装 LLM 多模态视觉调用
4. 创建 PIL Image 转 base64 编码的工具函数（放入 `server/src/lumina/vision/utils.py`）
5. 创建 `server/tests/test_ocr.py` — 使用样本图片测试 OCR 和视觉分析

## §6 Acceptance Criteria
- [ ] OCREngine 能从测试截图中识别出文字，返回带正确 bbox 的 OCRResult 列表
- [ ] OCREngine.find_text 能按目标字符串过滤 OCR 结果
- [ ] VisionAnalyzer.analyze_screen 将图片发送至 LLM 并返回文字描述
- [ ] VisionAnalyzer.find_element 能通过描述定位 UI 元素并返回 ElementLocation 列表
- [ ] PaddleOCR 模型仅在首次调用时加载，后续调用复用缓存实例
- [ ] 所有测试通过（OCR 测试可使用 fixture 图片）

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
