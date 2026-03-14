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

## 视觉工具 (Phase 05)

| 工具名 | 类 | 风险 | Origin Phase | 说明 |
|--------|-----|------|-------------|------|
| `capture_screen` | `CaptureScreenTool` | LOW | [Phase 05](../phases/phase_05_screen_vision.md) | 截图 + OCR，受 PrivacyGuard 保护 |
| `click_at` | `ClickAtTool` | MEDIUM | [Phase 05](../phases/phase_05_screen_vision.md) | 桌宠跑到坐标并点击 |
| `type_text` | `TypeTextTool` | LOW | [Phase 05](../phases/phase_05_screen_vision.md) | 在焦点位置输入文字 |
| `hotkey` | `HotkeyTool` | MEDIUM | [Phase 05](../phases/phase_05_screen_vision.md) | 执行快捷键组合 |
| `find_and_click` | `FindAndClickTool` | MEDIUM | [Phase 05](../phases/phase_05_screen_vision.md) | OCR 查找文字并点击 |

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
| `ScreenCapture` | `server/lumina/vision/capture.py` | [Phase 05](../phases/phase_05_screen_vision.md) | 基于 mss 的屏幕截图 |
| `OcrEngine` | `server/lumina/vision/ocr.py` | [Phase 05](../phases/phase_05_screen_vision.md) | PaddleOCR 封装，延迟加载 |
| `PhysicalInteraction` | `server/lumina/vision/interaction.py` | [Phase 05](../phases/phase_05_screen_vision.md) | pyautogui 物理操作封装 |
| `BrowserManager` | `server/lumina/tools/web/browser_manager.py` | [Phase 06](../phases/phase_06_web_automation.md) | Playwright 浏览器生命周期管理 |
| `ContentExtractor` | `server/lumina/tools/web/content_extractor.py` | [Phase 06](../phases/phase_06_web_automation.md) | 网页结构化内容提取 |
| `PrivacyGuard` | `server/lumina/security/privacy.py` | [Phase 07](../phases/phase_07_security_privacy.md) | 隐私保护：黑名单 + 遮罩 |
