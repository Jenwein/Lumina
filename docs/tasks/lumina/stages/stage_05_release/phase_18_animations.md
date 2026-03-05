# Phase 18: 动画状态机完善

## §1 Goal
完善桌宠全部动画状态：待机、移动、思考中、打字中、观察中、点击动作、庆祝、失败。

## §2 Dependencies
- **Prerequisite phases**: Phase 04, Phase 12
- **Source files to read**: `client/scripts/pet/pet_state_machine.gd`, `client/scripts/pet/pet_controller.gd`

## §3 Design & Constraints
- **Architecture principles**:
  - 完整状态机包含 8 个状态及其转换规则：
    - **IDLE**：默认休息状态，呼吸/轻微浮动的微妙待机动画
    - **MOVING**：向目标位置移动的行走/奔跑动画
    - **THINKING**：LLM 生成响应时的视觉指示（旋转/气泡）
    - **TYPING**：Agent 输出文本时的打字动画
    - **OBSERVING**：屏幕分析期间的观察/扫描动画
    - **CLICKING**：向目标位置伸手并按下的点击动画
    - **CELEBRATING**：任务成功时的庆祝动画（跳跃/舞蹈/闪光）
    - **FAILED**：出错时的沮丧/困惑动画
  - 使用 `AnimationPlayer` 或 `AnimatedSprite2D` 实现帧动画
  - 状态转换由 Python 后端通过 WebSocket 事件触发
  - 状态切换间实现平滑过渡混合
  - 占位动画使用简单的几何变换（缩放、旋转、颜色变化）
- **Boundary conditions**:
  - 每个状态必须有进入/退出动画钩子
  - 无效状态转换被静默拒绝并记录日志
  - 动画中断时从当前帧平滑过渡到新状态
- **Out of scope**: Spine/Live2D 集成（未来版本）、3D 模型、自定义角色美术

## §4 Interface Contract

```gdscript
# client/scripts/pet/pet_state_machine.gd (extended)
class_name PetStateMachine extends Node

enum State { IDLE, MOVING, THINKING, TYPING, OBSERVING, CLICKING, CELEBRATING, FAILED }

var current_state: State = State.IDLE

func transition_to(new_state: State) -> void: ...
func get_available_transitions() -> Array[State]: ...

signal state_entered(state: State)
signal state_exited(state: State)
```

```gdscript
# client/scripts/pet/pet_animator.gd
class_name PetAnimator extends Node

func play_state_animation(state: PetStateMachine.State) -> void: ...
func play_one_shot(animation_name: String) -> void: ...

signal animation_finished(animation_name: String)
```

**WebSocket 事件 → 状态映射**:
| WebSocket Event | Target State |
|-----------------|-------------|
| `agent_thinking` | THINKING |
| `agent_typing` | TYPING |
| `agent_observing` | OBSERVING |
| `agent_clicking` | CLICKING |
| `task_completed` | CELEBRATING |
| `task_failed` | FAILED |
| `agent_idle` | IDLE |

## §5 Implementation Steps
1. 扩展 `client/scripts/pet/pet_state_machine.gd`，添加全部 8 个状态及合法转换规则
2. 创建 `client/scripts/pet/pet_animator.gd` — 动画播放控制器
3. 使用 Tween 创建每个状态的占位动画（缩放弹跳、旋转、颜色渐变）
4. 更新 `pet.tscn` 场景，加入包含全部状态动画的 `AnimationPlayer`
5. 将 WebSocket 事件映射到状态转换（如 `agent_thinking` → THINKING）
6. 实现状态切换间的平滑过渡混合
7. 在 Agent 任务完成/失败时添加庆祝/失败动画触发

## §6 Acceptance Criteria
- [ ] 全部 8 个状态均有可见的占位动画
- [ ] 状态转换平滑，无视觉闪烁或跳变
- [ ] WebSocket 事件正确触发状态变更
- [ ] 无效状态转换被优雅拒绝（不崩溃）
- [ ] 任务成功时播放庆祝动画，出错时播放失败动画

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
