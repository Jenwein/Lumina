# Phase 09: 屏幕截取系统

## §1 Goal
实现跨平台屏幕截取能力，支持全屏、区域、指定显示器截图，输出 PIL Image 统一格式。

## §2 Dependencies
- **Prerequisite phases**: Phase 01
- **Source files to read**: `server/src/lumina/vision/`

## §3 Design & Constraints
- **Architecture principles**:
  - 使用 `mss` 库实现跨平台快速屏幕截取
  - 支持三种截取模式：全屏（任意显示器）、区域截取（x, y, w, h）、按索引指定显示器
  - 统一输出格式为 `PIL.Image.Image (RGB)`
  - MonitorInfo 数据模型：index, x, y, width, height, is_primary
  - 异步包装：通过 `run_in_executor` 将同步 mss 调用包装为 async 接口
  - mss 实例延迟初始化（lazy initialization），避免模块导入时的副作用
- **Boundary conditions**:
  - monitor_index=0 表示主显示器
  - 区域截取坐标为绝对屏幕坐标
  - CaptureResult 中 image 字段为 PIL.Image.Image 对象，不做序列化
  - timestamp 使用 `time.time()` 记录截取时刻
- **Out of scope**: OCR、图像分析、多显示器坐标映射（Phase 13）

## §4 Interface Contract

```python
# server/src/lumina/vision/models.py
from pydantic import BaseModel
from typing import Any

class MonitorInfo(BaseModel):
    index: int
    x: int
    y: int
    width: int
    height: int
    is_primary: bool

class CaptureResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    image: Any  # PIL.Image.Image (not serialized)
    monitor: MonitorInfo
    timestamp: float
```

```python
# server/src/lumina/vision/capture.py
from lumina.vision.models import MonitorInfo, CaptureResult
from PIL import Image

class ScreenCapture:
    async def capture_full(self, monitor_index: int = 0) -> CaptureResult:
        """截取指定显示器的完整屏幕。"""
        ...

    async def capture_region(self, x: int, y: int, w: int, h: int) -> CaptureResult:
        """截取屏幕上指定矩形区域。坐标为绝对屏幕坐标。"""
        ...

    async def get_monitors(self) -> list[MonitorInfo]:
        """枚举所有已连接的显示器信息。"""
        ...
```

## §5 Implementation Steps
1. 在 `server/pyproject.toml` 中添加 `mss` 和 `Pillow` 依赖
2. 创建 `server/src/lumina/vision/models.py` — 定义 MonitorInfo 和 CaptureResult 数据模型
3. 创建 `server/src/lumina/vision/capture.py` — 实现 ScreenCapture 类，包含 lazy mss 初始化和 async 包装
4. 创建 `server/tests/test_capture.py` — 测试显示器枚举、全屏截取、区域截取

## §6 Acceptance Criteria
- [ ] `get_monitors()` 返回所有已连接显示器的列表，MonitorInfo 字段正确
- [ ] `capture_full()` 返回有效 PIL Image，尺寸与显示器分辨率一致
- [ ] `capture_region()` 截取指定区域，返回 Image 尺寸与请求的 w×h 一致
- [ ] mss 实例在首次调用时才创建（lazy initialization）
- [ ] 所有测试通过：`uv run pytest server/tests/test_capture.py`

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
