# Changelog — Lumina

## 2026-03-14 — 初始化：设计文档体系搭建

### Delivered
- 创建完整的设计文档目录结构 (`docs/design/`)
- 编写 `master_overview.md` 作为项目唯一入口 (SSOT)
- 将项目拆解为 8 个阶段，分属 5 个 Stage，对齐 PRD 里程碑
- 初始化 `api_registry/` 四个模块接口文件骨架
- 编写全部 8 个阶段文档，定义接口契约和验收标准

### Decisions
- 采用 C/S 架构：Python 后端 (Logic Server) + Godot 前端 (Display Client)
- 通信协议选择 WebSocket + JSON，默认端口 8765
- Python 端采用 asyncio 异步架构
- Godot 端使用 GDScript，目标引擎版本 4.6.1
- LLM 集成统一使用 OpenAI 兼容 API 格式
- GLM-4-Flash 作为开发测试用模型
- 安全机制采用"高危操作拦截 + 用户物理确认"模式

### Deferred
- 具体的 2D 角色美术资源设计
- Spine/Live2D/VRM 等高级模型资产方案的技术选型细节
- CI/CD 流水线与自动化测试框架的具体配置
- 国际化 (i18n) 方案

---

*(Append new entries above this line)*
