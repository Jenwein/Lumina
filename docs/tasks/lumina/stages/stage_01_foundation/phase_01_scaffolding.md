# Phase 01: 项目脚手架与环境搭建

## §1 Goal
搭建 Python (uv + FastAPI) 后端和 Godot 4.x 前端的项目骨架，确保两端可独立启动。

## §2 Dependencies
- **Prerequisite phases**: None
- **Source files to read**: `PRD.md`, `docs/tasks/lumina/master_overview.md`

## §3 Design & Constraints
- **Architecture principles**:
  - `server/` 目录承载 Python 后端，`client/` 目录承载 Godot 前端
  - Python 使用 uv 管理项目，采用 src layout (`server/src/lumina/`)
  - FastAPI 作为 HTTP/WebSocket 入口
  - Godot 项目包含 `project.godot`、`scenes/`、`scripts/`、`assets/` 标准目录结构
  - 后端模块化拆分：`agent/`、`llm/`、`tools/`、`vision/`、`ws/`、`config/`
- **Boundary conditions**:
  - Python >= 3.11，Godot 4.x
  - uv 作为唯一 Python 包管理和虚拟环境工具
  - 所有模块包含 `__init__.py`，即使暂时为空
- **Out of scope**: 任何业务逻辑、WebSocket 通信实现、UI 渲染

## §4 Interface Contract

### Python 后端

```python
# server/src/lumina/main.py
from fastapi import FastAPI

app = FastAPI(title="Lumina", version="0.1.0")

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
```

- **启动命令**: `uv run uvicorn lumina.main:app --host 127.0.0.1 --port 8000`
- **模块入口**: `uv run python -m lumina`

### Godot 前端

- `client/project.godot` — Godot 4.x 项目文件，配置透明窗口、始终置顶
- 目录结构：`scenes/`、`scripts/`、`assets/`、`addons/`

## §5 Implementation Steps
1. 创建 `server/pyproject.toml`，声明依赖：fastapi、uvicorn、websockets、pydantic、pytest（dev）
2. 创建 `server/src/lumina/__init__.py`，写入 `__version__ = "0.1.0"`
3. 创建 `server/src/lumina/main.py`，包含最小化 FastAPI app 和 `/health` 端点
4. 创建 `server/src/lumina/__main__.py`，支持 `python -m lumina` 启动
5. 为每个子模块创建空 `__init__.py`：`agent/`、`llm/`、`tools/`、`vision/`、`ws/`、`config/`
6. 创建 `server/tests/__init__.py` 和 `server/tests/conftest.py`（含 FastAPI TestClient fixture）
7. 创建 `client/project.godot`，配置 Godot 4.x 设置（透明窗口、始终置顶、无边框）
8. 创建 `client/` 目录结构：`scenes/`、`scripts/`、`assets/`、`addons/`

## §6 Acceptance Criteria
- [ ] `uv sync` 在 `server/` 目录下成功执行，无报错
- [ ] `uv run pytest` 在 `server/` 目录下运行通过（即使没有测试用例也不报错）
- [ ] `uv run uvicorn lumina.main:app` 启动后，`GET /health` 返回 HTTP 200 `{"status": "ok"}`
- [ ] Godot 4.x 编辑器可无报错打开 `client/project.godot`
- [ ] 所有子模块目录（`agent/`、`llm/`、`tools/`、`vision/`、`ws/`、`config/`）均已创建且包含 `__init__.py`
- [ ] 项目根目录结构清晰：`server/` 和 `client/` 分离

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
