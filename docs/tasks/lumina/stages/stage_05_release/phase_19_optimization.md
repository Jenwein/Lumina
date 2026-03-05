# Phase 19: 资源优化与打包

## §1 Goal
实现低功耗模式、帧率管理，完成跨平台应用打包和用户文档编写。

## §2 Dependencies
- **Prerequisite phases**: Phase 01–18（全部前置阶段）
- **Source files to read**: 全部项目文件

## §3 Design & Constraints
- **Architecture principles**:
  - 低功耗模式：桌宠处于 idle 且无活动任务时，将 Godot 渲染帧率降至 5–10 FPS
  - 仅在活跃动画或用户交互期间使用完整帧率
  - Python 端：idle 时降低轮询频率，重型模块（PaddleOCR）延迟加载
  - 打包方案：
    - Python：使用 PyInstaller 或 Nuitka 构建独立可执行文件
    - Godot：导出模板适配 Windows（.exe）、macOS（.app/.dmg）、Linux（.AppImage）
    - 单一启动器/安装器，同时启动 Python 后端和 Godot 前端
  - 用户文档：README 包含安装指南、使用说明、配置参考
  - 项目结构应为未来添加自动更新预留扩展空间
- **Boundary conditions**:
  - 低功耗模式切换延迟不超过 100ms
  - 独立可执行文件大小应尽量控制（Python 端 < 200MB，Godot 端 < 100MB）
  - 启动器需处理后端启动失败的情况（端口占用、依赖缺失等）
- **Out of scope**: 自动更新机制、应用商店分发、CI/CD 流水线

## §4 Interface Contract

```python
# server/src/lumina/config/power.py
from typing import Literal
from pydantic import BaseModel

class PowerConfig(BaseModel):
    idle_timeout_seconds: int = 60
    low_power_fps: int = 5
    active_fps: int = 60

class PowerManager:
    def __init__(self, config: PowerConfig) -> None: ...
    def set_mode(self, mode: Literal["active", "idle", "low_power"]) -> None: ...
    def get_mode(self) -> str: ...
```

```gdscript
# client/scripts/system/power_manager.gd
class_name PowerManager extends Node

func set_target_fps(fps: int) -> void: ...
func on_activity_detected() -> void: ...
func on_idle_timeout() -> void: ...
```

**启动器接口**:
```
lumina-launcher[.exe]
  ├── 启动 Python 后端（子进程）
  ├── 等待后端 health check 通过
  ├── 启动 Godot 前端
  └── 监听退出信号 → 优雅关闭两端
```

## §5 Implementation Steps
1. 创建 `server/src/lumina/config/power.py` — 实现后端 `PowerManager`，控制资源使用
2. 创建 `client/scripts/system/power_manager.gd` — 基于活动状态的帧率管理
3. 实现 idle 检测：无用户交互或 Agent 活动超过 N 秒 → 切换低功耗模式
4. 配置 PyInstaller spec 文件用于 Python 后端打包
5. 配置 Godot 导出预设（Windows、macOS、Linux）
6. 创建启动器脚本，同时启动后端与前端，处理优雅关闭
7. 编写完整的 `README.md`，包含安装、使用和配置文档
8. 创建 `CONTRIBUTING.md`，包含开发环境搭建指南

## §6 Acceptance Criteria
- [ ] idle 状态下桌宠帧率降至配置的低功耗值
- [ ] 检测到活动后立即恢复正常帧率
- [ ] Python 后端构建为独立可执行文件（无需用户安装 Python）
- [ ] Godot 导出可在 Windows、macOS、Linux 三个平台运行
- [ ] 启动器同时启动两个组件并处理优雅关闭
- [ ] README 覆盖安装、配置和基本使用说明
- [ ] 优化变更后全部已有测试仍然通过

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
