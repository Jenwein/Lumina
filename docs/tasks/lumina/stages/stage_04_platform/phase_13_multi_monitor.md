# Phase 13: 多显示器支持

## §1 Goal
实现所有连接显示器的统一坐标系映射，桌宠可跨屏移动和操作。

## §2 Dependencies
- **Prerequisite phases**: Phase 09, Phase 04
- **Source files to read**: `server/src/lumina/vision/capture.py`, `client/scripts/pet/pet_controller.gd`

## §3 Design & Constraints
- **Architecture principles**:
  - Python 端：从所有显示器构建统一坐标映射（虚拟桌面空间）
  - 启动时及显示器配置变化时，通过 WebSocket 将显示器布局同步给 Godot
  - Godot 端：窗口跨越所有显示器（或在显示器间移动）
  - 桌宠移动支持跨显示器坐标
  - 所有工具坐标统一在虚拟桌面坐标空间中操作
- **Boundary conditions**:
  - virtual_origin 可能为负值（Windows 允许显示器位于主屏左侧/上方）
  - 显示器间可能存在间隙（非连续区域），桌宠路径规划需处理
  - `virtual_to_screen` 返回值包含 monitor_index，方便后续截取指定显示器
  - 热插拔仅记录日志并通知，不自动重建坐标系
- **Out of scope**: 每显示器独立 DPI 缩放适配（延后处理）、热插拔自动检测

## §4 Interface Contract

```python
# server/src/lumina/vision/monitor_map.py
from pydantic import BaseModel
from lumina.vision.models import MonitorInfo

class MonitorLayout(BaseModel):
    monitors: list[MonitorInfo]
    virtual_width: int
    virtual_height: int
    virtual_origin: tuple[int, int]  # 虚拟桌面左上角坐标（可能为负值）

class MonitorMapper:
    async def refresh(self) -> MonitorLayout:
        """刷新显示器信息，重建统一坐标映射。"""
        ...

    def screen_to_virtual(self, monitor_index: int, x: int, y: int) -> tuple[int, int]:
        """将指定显示器的本地坐标转换为虚拟桌面坐标。"""
        ...

    def virtual_to_screen(self, vx: int, vy: int) -> tuple[int, int, int]:
        """将虚拟桌面坐标转换为 (monitor_index, local_x, local_y)。"""
        ...
```

```python
# WebSocket command payloads
{"action": "sync_monitors", "payload": {
    "monitors": [{"index": 0, "x": 0, "y": 0, "width": 1920, "height": 1080, "is_primary": true}, ...],
    "virtual_width": 3840,
    "virtual_height": 1080,
    "virtual_origin": [0, 0]
}}
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/vision/monitor_map.py` — MonitorMapper 含坐标转换逻辑
2. 在 WebSocket 协议中添加 `sync_monitors` 命令，将显示器布局推送给 Godot
3. 更新 `client/scripts/pet/pet_controller.gd` 以处理跨显示器坐标和窗口移动
4. 更新 ScreenCapture，使截取坐标与统一坐标空间一致
5. 创建 `server/tests/test_monitor_map.py` — 使用多显示器 fixture 测试坐标转换

## §6 Acceptance Criteria
- [ ] MonitorMapper 在多显示器配置下正确映射坐标
- [ ] `screen_to_virtual` 和 `virtual_to_screen` 互为逆运算
- [ ] 显示器布局在 WebSocket 连接建立时同步给 Godot
- [ ] 桌宠可在多个显示器间平滑移动
- [ ] 截屏坐标与统一坐标空间一致
- [ ] 测试通过（使用模拟的多显示器布局）

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
