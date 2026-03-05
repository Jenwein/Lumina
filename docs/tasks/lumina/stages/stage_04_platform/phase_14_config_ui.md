# Phase 14: 配置界面

## §1 Goal
在 Godot 中实现设置面板，支持 API 节点管理（增删改）、模型切换、系统参数配置。

## §2 Dependencies
- **Prerequisite phases**: Phase 05, Phase 08
- **Source files to read**: `client/scripts/ui/context_menu.gd`, `server/src/lumina/llm/manager.py`, `server/src/lumina/config/`

## §3 Design & Constraints
- **Architecture principles**:
  - Godot 设置面板：独立场景，覆盖在主窗口之上
  - 分区设计：LLM Providers（增/删/改/测试）、Active Model 选择器、System Prompt 编辑器、General（端口、桌宠速度等）
  - 设置通过 Python 后端持久化（YAML 配置文件）
  - WebSocket 命令：get_config, update_config, test_provider, list_providers
  - 从右键菜单 "Settings" 入口打开设置面板
- **Boundary conditions**:
  - 设置面板打开时桌宠交互暂停（避免冲突）
  - Provider 测试发送简短测试消息并报告连通性（成功/失败 + 延迟）
  - 配置更新即时生效，无需重启后端
  - YAML 配置文件路径：`server/config/settings.yaml`
  - 敏感字段（API Key）在 UI 中部分遮蔽显示
- **Out of scope**: 主题定制、每显示器独立设置、高级 Prompt 模板系统

## §4 Interface Contract

```gdscript
# client/scripts/ui/settings_panel.gd
class_name SettingsPanel extends Control

func open() -> void:
    ## 显示设置面板，从后端加载当前配置。
    pass

func close() -> void:
    ## 关闭设置面板，恢复桌宠交互。
    pass

func load_config(config: Dictionary) -> void:
    ## 将后端返回的配置数据填充到 UI 控件。
    pass

signal config_changed(key: String, value: Variant)
signal provider_test_requested(provider_name: String)
```

```python
# WebSocket command payloads

# 获取完整配置
{"action": "get_config", "payload": {}}
# 响应: {"action": "config_data", "payload": {"llm": {...}, "general": {...}, "system_prompt": "..."}}

# 更新单项配置
{"action": "update_config", "payload": {"section": "llm", "key": "active_provider", "value": "deepseek"}}
# 响应: {"action": "config_updated", "payload": {"success": true}}

# 测试 Provider 连通性
{"action": "test_provider", "payload": {"name": "deepseek"}}
# 响应: {"action": "provider_test_result", "payload": {"name": "deepseek", "success": true, "latency_ms": 320}}

# 列出所有已配置 Provider
{"action": "list_providers", "payload": {}}
# 响应: {"action": "providers_list", "payload": {"providers": [{"name": "deepseek", "base_url": "...", "active": true}, ...]}}
```

## §5 Implementation Steps
1. 创建 `client/scenes/ui/settings_panel.tscn` — 分 Tab 的设置界面（Providers / Model / Prompt / General）
2. 创建 `client/scripts/ui/settings_panel.gd` — 面板逻辑：配置加载、展示、编辑、保存
3. 创建 `client/scripts/ui/provider_editor.gd` — LLM Provider 增/删/改表单组件
4. 在 `server/src/lumina/ws/` 中添加 config 相关的 WebSocket 命令处理器
5. 创建 `server/src/lumina/config/settings.py` — 配置持久化（YAML 读写）
6. 在右键菜单中添加 "Settings" 选项，点击后打开设置面板

## §6 Acceptance Criteria
- [ ] 设置面板从右键菜单成功打开
- [ ] 可增加、编辑、删除 LLM Provider
- [ ] Provider 连通性测试可执行（发送测试消息，报告成功/失败）
- [ ] Active Model 切换即时生效
- [ ] 配置变更持久化到 YAML 文件，重启后保持不变
- [ ] System Prompt 可编辑并保存
- [ ] API Key 在 UI 中部分遮蔽显示

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
