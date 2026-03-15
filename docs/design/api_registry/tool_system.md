# API Registry — 工具系统

> 本文档记录工具系统框架和所有已注册工具的接口。

## 框架接口

| Interface | File Path | Origin Phase (Link) | Usage Note |
|-----------|-----------|---------------------|------------|
| `RiskLevel` | `server/lumina/tools/base.py` | [Phase 04](../phases/phase_04_tool_system.md) | 风险等级枚举: LOW / MEDIUM / HIGH |
| `BaseTool` | `server/lumina/tools/base.py` | [Phase 04](../phases/phase_04_tool_system.md) | 工具抽象基类。子类实现 `execute(**kwargs) -> str` |
| `BaseTool.to_tool_definition` | `server/lumina/tools/base.py` | [Phase 04](../phases/phase_04_tool_system.md) | 转为 LLM Function Calling 格式 |
| `ToolRegistry` | `server/lumina/tools/registry.py` | [Phase 04](../phases/phase_04_tool_system.md) | 工具注册/发现/执行中心 |
| `ToolRegistry.execute` | `server/lumina/tools/registry.py` | [Phase 04](../phases/phase_04_tool_system.md) | 按名称查找工具并执行，Phase 07 后经过 SecurityInterceptor |
| `SecurityInterceptor` | `server/lumina/security/interceptor.py` | [Phase 07](../phases/phase_07_security_privacy.md) | 安全拦截层，HIGH 风险需用户确认后执行 |

## 系统工具 (Phase 04)

| 工具名 | 类 | 风险 | Origin Phase | 说明 |
|--------|-----|------|-------------|------|
| `read_file` | `ReadFileTool` | LOW | [Phase 04](../phases/phase_04_tool_system.md) | 读取文件文本内容 |
| `write_file` | `WriteFileTool` | MEDIUM | [Phase 04](../phases/phase_04_tool_system.md) | 写入文件 |
| `list_directory` | `ListDirectoryTool` | LOW | [Phase 04](../phases/phase_04_tool_system.md) | 列出目录内容 |
| `create_directory` | `CreateDirectoryTool` | LOW | [Phase 04](../phases/phase_04_tool_system.md) | 创建目录 |
| `delete_file` | `DeleteFileTool` | HIGH | [Phase 04](../phases/phase_04_tool_system.md) | 删除文件 (不可撤销) |
| `move_file` | `MoveFileTool` | MEDIUM | [Phase 04](../phases/phase_04_tool_system.md) | 移动/重命名 |
| `launch_app` | `LaunchAppTool` | MEDIUM | [Phase 04](../phases/phase_04_tool_system.md) | 启动应用程序 |
| `close_app` | `CloseAppTool` | MEDIUM | [Phase 04](../phases/phase_04_tool_system.md) | 关闭应用进程 |
| `get_system_info` | `GetSystemInfoTool` | LOW | [Phase 04](../phases/phase_04_tool_system.md) | 获取 OS/CPU/内存等系统信息 |
| `get_running_processes` | `GetRunningProcessesTool` | LOW | [Phase 04](../phases/phase_04_tool_system.md) | 获取进程列表 |

## 用户交互工具 (Phase 04)

| 工具名 | 类 | 风险 | Origin Phase | 说明 |
|--------|-----|------|-------------|------|
| `ask_user` | `AskUserTool` | LOW | [Phase 04](../phases/phase_04_tool_system.md) | Agent 向用户提问并等待回复。支持自由文本和选择题。通过 `user_prompt` / `user_prompt_response` WebSocket 消息实现 |
| `notify_user` | `NotifyUserTool` | LOW | [Phase 04](../phases/phase_04_tool_system.md) | Agent 向用户展示通知信息，不等待回复。通过 `show_bubble` pet_command 实现 |

## 视觉工具 (Phase 05)

| 工具名 | 类 | 风险 | Origin Phase | 说明 |
|--------|-----|------|-------------|------|
| `inspect_window` | `InspectWindowTool` | LOW | [Phase 05](../phases/phase_05_screen_vision.md) | 三级感知(UIA→OCR→AI)扫描活动窗口元素，返回比例坐标 |
| `visual_locate` | `VisualLocateTool` | LOW | [Phase 05](../phases/phase_05_screen_vision.md) | AI 视觉分析兜底，定位图标/无标签控件(需模型支持图像) |
| `click_at` | `ClickAtTool` | MEDIUM | [Phase 05](../phases/phase_05_screen_vision.md) | 按比例坐标(0.0~1.0)点击活动窗口元素，驱动桌宠跑过去点击 |
| `type_text` | `TypeTextTool` | LOW | [Phase 05](../phases/phase_05_screen_vision.md) | 在当前焦点位置输入文字 |
| `hotkey` | `HotkeyTool` | MEDIUM | [Phase 05](../phases/phase_05_screen_vision.md) | 执行快捷键组合 |

## Web 工具 (Phase 06)

| 工具名 | 类 | 风险 | Origin Phase | 说明 |
|--------|-----|------|-------------|------|
| `web_navigate` | `WebNavigateTool` | LOW | [Phase 06](../phases/phase_06_web_automation.md) | 打开 URL 并返回页面摘要 |
| `web_search` | `WebSearchTool` | LOW | [Phase 06](../phases/phase_06_web_automation.md) | 搜索引擎查询 |
| `web_read_page` | `WebReadPageTool` | LOW | [Phase 06](../phases/phase_06_web_automation.md) | 读取当前页面内容 |
| `web_click` | `WebClickTool` | LOW | [Phase 06](../phases/phase_06_web_automation.md) | 点击页面元素 |
| `web_fill` | `WebFillTool` | LOW | [Phase 06](../phases/phase_06_web_automation.md) | 填写表单输入框 |
| `web_screenshot` | `WebScreenshotTool` | LOW | [Phase 06](../phases/phase_06_web_automation.md) | 截取页面截图 |

## 支撑模块

| Interface | File Path | Origin Phase (Link) | Usage Note |
|-----------|-----------|---------------------|------------|
| `WindowManager` | `server/lumina/vision/window_info.py` | [Phase 05](../phases/phase_05_screen_vision.md) | 活动窗口查找/激活/矩形获取 (win32gui) |
| `CoordinateConverter` | `server/lumina/vision/coordinates.py` | [Phase 05](../phases/phase_05_screen_vision.md) | 比例坐标(0~1) ↔ 屏幕像素的双向换算 |
| `UIAutomationScanner` | `server/lumina/vision/ui_automation.py` | [Phase 05](../phases/phase_05_screen_vision.md) | Tier 1: Windows UIA 元素树扫描 |
| `ScreenCapture` | `server/lumina/vision/capture.py` | [Phase 05](../phases/phase_05_screen_vision.md) | Tier 2: 活动窗口区域截图 + 缩放 (mss) |
| `OcrEngine` | `server/lumina/vision/ocr.py` | [Phase 05](../phases/phase_05_screen_vision.md) | Tier 2: PaddleOCR 封装，延迟加载，结果含比例坐标 |
| `AIVisualAnalyzer` | `server/lumina/vision/ai_visual.py` | [Phase 05](../phases/phase_05_screen_vision.md) | Tier 3: 多模态截图分析兜底，需模型支持图像 |
| `WindowPerceiver` | `server/lumina/vision/perceiver.py` | [Phase 05](../phases/phase_05_screen_vision.md) | 三级感知编排器: UIA → OCR → AI 视觉 |
| `PhysicalInteraction` | `server/lumina/vision/interaction.py` | [Phase 05](../phases/phase_05_screen_vision.md) | pyautogui 物理操作封装 |
| `BrowserManager` | `server/lumina/tools/web/browser_manager.py` | [Phase 06](../phases/phase_06_web_automation.md) | Playwright 浏览器生命周期管理 |
| `ContentExtractor` | `server/lumina/tools/web/content_extractor.py` | [Phase 06](../phases/phase_06_web_automation.md) | 网页结构化内容提取 |
| `PrivacyGuard` | `server/lumina/security/privacy.py` | [Phase 07](../phases/phase_07_security_privacy.md) | 隐私保护：黑名单 + 遮罩 |
