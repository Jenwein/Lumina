# Phase 16: 安全与确认机制

## §1 Goal
实现高危操作拦截系统和单步执行模式，保护用户系统免受意外破坏。

## §2 Dependencies
- **Prerequisite phases**: Phase 06, Phase 08
- **Source files to read**: `server/src/lumina/agent/engine.py`, `server/src/lumina/tools/`, `client/scripts/ui/dialogue_bubble.gd`

## §3 Design & Constraints
- **Architecture principles**:
  - Danger classifier：基于可配置规则将工具调用分为 safe / warning / dangerous 三级
  - Dangerous 操作包括：文件删除、格式化命令、敏感终端命令、注册表编辑
  - Warning 操作包括：文件覆写、应用终止、批量操作
  - 当检测到 dangerous 操作时，暂停执行，通过 WebSocket 向 Godot 发送确认请求
  - Godot 显示醒目的确认气泡，附带操作描述；用户必须物理点击桌宠进行确认
  - Single-step 模式：无论危险等级，每个工具调用均暂停等待确认
  - 危险规则通过 YAML 文件配置
  - 超时机制：若在可配置超时时间内未收到确认，自动中止操作
- **Boundary conditions**:
  - 确认请求必须包含可读的操作描述（工具名 + 参数摘要）
  - 超时默认值 30 秒，可通过配置调整
  - WebSocket 断连期间所有 dangerous 操作自动拒绝
- **Out of scope**: Undo/rollback 系统、沙箱化执行

## §4 Interface Contract

```python
# server/src/lumina/agent/safety.py
from enum import Enum
from typing import Any

class DangerLevel(str, Enum):
    SAFE = "safe"
    WARNING = "warning"
    DANGEROUS = "dangerous"

class SafetyClassifier:
    def __init__(self, rules_path: str) -> None: ...
    def classify(self, tool_name: str, arguments: dict[str, Any]) -> DangerLevel: ...
    def get_description(self, tool_name: str, arguments: dict[str, Any]) -> str: ...

class SafetyGuard:
    def __init__(
        self,
        classifier: SafetyClassifier,
        ws_manager: "ConnectionManager",
        single_step: bool = False,
    ) -> None: ...
    async def check_and_confirm(self, tool_name: str, arguments: dict[str, Any]) -> bool: ...
    def set_single_step(self, enabled: bool) -> None: ...
```

```gdscript
# client/scripts/ui/confirmation_bubble.gd
class_name ConfirmationBubble extends Control

func show_confirmation(action_desc: String, danger_level: String) -> void: ...

signal confirmed()
signal rejected()
```

**WebSocket 命令**:
| Direction | Command | Payload |
|-----------|---------|---------|
| Server → Client | `request_confirmation` | `{ "action": str, "danger_level": str, "timeout": int }` |
| Client → Server | `confirmation_response` | `{ "confirmed": bool }` |

## §5 Implementation Steps
1. 创建 `server/src/lumina/agent/safety.py` — 实现 `SafetyClassifier` 和 `SafetyGuard`
2. 创建 `server/config/safety_rules.yaml` — 默认危险分类规则（工具名 → 等级映射 + 参数匹配规则）
3. 将 `SafetyGuard` 集成到 `AgentEngine` 的工具执行路径中，在调用工具前进行拦截
4. 创建 `client/scenes/ui/confirmation_bubble.tscn` — 醒目的确认 UI 场景
5. 创建 `client/scripts/ui/confirmation_bubble.gd` — 实现确认/拒绝交互逻辑
6. 添加 WebSocket 命令：`request_confirmation`（服务端→客户端）、`confirmation_response`（客户端→服务端）
7. 创建 `server/tests/test_safety.py` — 测试分类逻辑和确认流程

## §6 Acceptance Criteria
- [ ] 文件删除操作被分类为 DANGEROUS，文件读取操作被分类为 SAFE
- [ ] Dangerous 操作暂停 Agent 执行并向 Godot 发送确认请求
- [ ] 用户点击桌宠确认后，操作继续执行
- [ ] 用户拒绝或超时后，操作被中止
- [ ] Single-step 模式下每个工具调用都暂停等待确认
- [ ] 所有测试通过

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
