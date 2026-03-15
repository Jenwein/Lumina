# Phase 06: Web 自动化

## §1 Goal

集成 Playwright 浏览器自动化引擎，为 Agent 提供 Web 操控能力——包括静默后台操作（爬取信息、自动填表）和可见浏览器操作（用户可观察的网页交互）。本阶段以工具形式接入 Agent，使其在 ReAct 循环中能自主选择使用浏览器。

## §2 Dependencies

- **Prerequisite phases**: Phase 04 (`[x] Done`)
- **Reference Materials**:
    - [ ] [PRD — Web 自动化工具](../../../PRD.md) §2.2
    - [ ] [Playwright Python 文档](https://playwright.dev/python/docs/intro)
- **Source files to read**:
    - [ ] `server/lumina/tools/base.py` (Phase 04 — BaseTool)
    - [ ] `server/lumina/tools/registry.py` (Phase 04 — ToolRegistry)
    - [ ] `server/lumina/agent/core.py` (Phase 03 — AgentCore)

## §3 Design & Constraints

### 运行模式

| 模式 | headless | 场景 |
|------|----------|------|
| **静默模式** | `True` | 后台抓取信息、API 不可用时的网页查询 |
| **可见模式** | `False` | 用户要求"帮我打开网页做某事"，需视觉反馈 |

默认使用静默模式，用户可通过对话指定可见模式。

### 浏览器生命周期

```
Agent 首次调用 Web 工具
       │
       ▼
BrowserManager.ensure_browser()
       │
       ├── 已有浏览器实例 → 复用
       │
       └── 无 → 启动 Chromium (Playwright)
              │
              ▼
         创建 BrowserContext (隔离会话)
              │
              ▼
         返回 Page 对象
              │
       ┌──────┴──────┐
       │   操作网页   │
       └──────┬──────┘
              │
         闲置超时 (5min) → 自动关闭浏览器释放资源
```

**关键约束**:
- 同时只维护一个 Browser 实例，多个工具调用复用同一实例
- BrowserContext 提供 Cookie/Session 隔离
- 闲置超过 5 分钟自动关闭（可配置）
- 浏览器崩溃后自动恢复

### 工具设计

Web 工具采用高级抽象，Agent 无需了解 CSS 选择器等底层细节：

| 工具 | 功能 | 描述 |
|------|------|------|
| `web_navigate` | 导航到 URL | 打开指定网页并返回页面标题和主要文本内容 |
| `web_search` | 搜索引擎查询 | 通过搜索引擎查找信息，返回搜索结果摘要 |
| `web_read_page` | 读取页面内容 | 提取当前页面的结构化文本内容 |
| `web_click` | 点击元素 | 通过文本内容或描述定位并点击页面元素 |
| `web_fill` | 填写表单 | 在输入框中填入文字 |
| `web_screenshot` | 页面截图 | 截取当前页面截图并描述内容 |

### Architecture Principles

- **资源可控**: 浏览器实例有明确的生命周期管理，避免内存泄漏
- **容错设计**: 网络超时、页面加载失败等常见问题有优雅处理
- **内容提取**: 页面内容提取使用结构化方式（提取正文、去除广告/导航），而非返回原始 HTML
- **安全限制**: 不自动保存密码，不访问 file:// 协议

### Out of scope

- 复杂的多标签页管理（本阶段仅支持单页面操作）
- Cookie / Session 持久化
- 代理配置和认证
- 下载文件管理

## §4 Interface Contract

```python
# server/lumina/tools/web/browser_manager.py

class BrowserManager:
    """管理 Playwright 浏览器实例的生命周期。"""

    def __init__(self, headless: bool = True, idle_timeout: float = 300.0) -> None: ...

    async def ensure_browser(self) -> None:
        """确保浏览器已启动。"""
        ...

    async def get_page(self) -> "Page":
        """获取当前活跃的页面。"""
        ...

    async def close(self) -> None:
        """关闭浏览器并释放资源。"""
        ...

    @property
    def is_active(self) -> bool: ...


# server/lumina/tools/web/content_extractor.py

class ContentExtractor:
    """从网页中提取结构化文本内容。"""

    @staticmethod
    async def extract_text(page: "Page", max_length: int = 4000) -> str:
        """提取页面主要文本内容，去除导航、广告等干扰。"""
        ...

    @staticmethod
    async def extract_links(page: "Page") -> list[dict[str, str]]:
        """提取页面链接 [{"text": "...", "href": "..."}]。"""
        ...


# server/lumina/tools/web/web_tools.py

class WebNavigateTool(BaseTool):
    name = "web_navigate"
    description = "在浏览器中打开指定 URL，返回页面标题和主要文本内容摘要。"
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "要访问的网页 URL"},
            "visible": {"type": "boolean", "description": "是否显示浏览器窗口，默认 false"}
        },
        "required": ["url"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, url: str, visible: bool = False) -> str: ...


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "使用搜索引擎搜索关键词，返回前 5 条搜索结果的标题和摘要。"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
        "required": ["query"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, query: str) -> str: ...


class WebReadPageTool(BaseTool):
    name = "web_read_page"
    description = "读取当前浏览器页面的文本内容。需先用 web_navigate 打开页面。"
    risk_level = RiskLevel.LOW

    async def execute(self) -> str: ...


class WebClickTool(BaseTool):
    name = "web_click"
    description = "点击当前页面上包含指定文本的元素（按钮、链接等）。"
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "要点击的元素的文本内容"}
        },
        "required": ["text"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, text: str) -> str: ...


class WebFillTool(BaseTool):
    name = "web_fill"
    description = "在当前页面的输入框中填入文字。通过 placeholder 或 label 文本定位输入框。"
    parameters = {
        "type": "object",
        "properties": {
            "locator": {"type": "string", "description": "输入框的 placeholder 或关联 label 文本"},
            "value": {"type": "string", "description": "要填入的文字"}
        },
        "required": ["locator", "value"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, locator: str, value: str) -> str: ...


class WebScreenshotTool(BaseTool):
    name = "web_screenshot"
    description = "截取当前浏览器页面的截图，返回页面的视觉描述。"
    risk_level = RiskLevel.LOW

    async def execute(self) -> str: ...
```

## §5 Implementation Steps

1. **安装依赖**: 添加 `playwright` 到 `pyproject.toml`，运行 `playwright install chromium`。
2. **实现浏览器管理器** (`server/lumina/tools/web/browser_manager.py`): 生命周期管理、闲置超时、崩溃恢复。
3. **实现内容提取器** (`server/lumina/tools/web/content_extractor.py`): 从页面 DOM 中提取结构化文本。
4. **实现 Web 工具集** (`server/lumina/tools/web/web_tools.py`): 6 个工具类。
5. **注册到 Agent**: 在启动时注册所有 Web 工具。
6. **编写测试** (`server/tests/test_web_tools.py`): 测试导航、搜索、内容提取（使用 mock 或本地 HTML）。
7. **端到端验证**: "帮我搜索今天的天气" → Agent 自动调用 `web_search` → 返回结果。

## §6 Acceptance Criteria

**⚠ MANDATORY: Every item must be verified and checked `[x]` before proceeding to §7.**

### Functional Verification
- [ ] `BrowserManager.ensure_browser()` 能正确启动 Chromium 实例
- [ ] `BrowserManager.close()` 能干净关闭浏览器并释放资源
- [ ] 闲置超过 5 分钟后浏览器自动关闭 (验证 `idle_timeout` 逻辑)
- [ ] 浏览器崩溃后 `ensure_browser()` 能自动恢复
- [ ] `web_navigate` 能打开网页并返回页面标题和主要内容摘要
- [ ] `web_search` 能执行搜索引擎查询并返回前 5 条结构化结果
- [ ] `web_click` 能通过文本内容定位并点击页面元素 (按钮/链接)
- [ ] `web_fill` 能通过 placeholder/label 定位输入框并填入文字
- [ ] `web_screenshot` 能截取页面截图
- [ ] `visible=true` 时浏览器窗口正常显示
- [ ] `ContentExtractor.extract_text()` 能提取页面正文并去除导航/广告

### Test Verification
- [ ] 单元测试 `pytest server/tests/test_web_tools.py` 通过，0 failures
- [ ] 测试覆盖: `BrowserManager` 生命周期、`ContentExtractor`、各工具的正常/异常路径

### Integration Verification
- [ ] 端到端: Godot 发送 "帮我搜索今天的天气" → Agent 自动选择 `web_search` → 返回搜索结果

### Code Quality
- [ ] `server/lumina/tools/web/` 下所有文件无 linter 错误

## §7 State Teardown Checklist

**⚠ MANDATORY: Every item is a concrete action. Complete each one and check `[x]`.**

- [ ] **§3/§4 Updated**: 若实现中设计/接口有变，更新本文档 §3 和 §4 使其与最终代码一致
- [ ] **changelog.md**: 追加本阶段条目 (Delivered/Decisions/Deferred) → `../changelog.md`
- [ ] **api_registry/tool_system.md**: 新增 Web 工具 (6个) 和 `BrowserManager`/`ContentExtractor` 支撑模块 → `../api_registry/tool_system.md`
- [ ] **master_overview.md**: 将 Phase 06 状态改为 `[x] Done` → `../master_overview.md`
- [ ] **§2 checkboxes**: 将本文档 §2 中所有 Reference Materials 和 Source files 标记为 `[x]`
