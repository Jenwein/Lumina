# Task Architect — Document Templates

## Master Overview Template

```markdown
# Task: [Task Name]

## Meta
- **Created**: [date]
- **Last Updated**: [date]
- **Status**: In Progress | Completed | Blocked
- **Complexity**: Moderate | High

## Documentation Index
- **Changelog**: [changelog.md](./changelog.md)
- **API Registry**: [Index](./api_registry/)
  - [Module A](./api_registry/module_a.md)
  - [Module B](./api_registry/module_b.md)

## Objective
[1–2 sentences describing the overall goal and deliverable]

## Constraints & Architecture Decisions
- [Key constraint or decision 1]
- [Key constraint or decision 2]

## Phase Map

### Stage 1: [Label] *(omit stage grouping for moderate tasks)*

| Phase | Title | Status | Dependencies | File |
|-------|-------|--------|--------------|------|
| 01 | [Data Model] | [ ] Pending | — | [phase_01.md](./stages/stage_01_label/phase_01_label.md) |
| 02 | [Interfaces] | [ ] Pending | Phase 01 | [phase_02.md](./stages/stage_01_label/phase_02_label.md) |
| 03 | [Implementation] | [ ] Pending | Phase 01, 02 | [phase_03.md](./stages/stage_01_label/phase_03_label.md) |

### Stage 2: [Label]

| Phase | Title | Status | Dependencies | File |
|-------|-------|--------|--------------|------|
| 04 | [Integration] | [ ] Pending | Phase 03 | [phase_04.md](./stages/stage_02_label/phase_04_label.md) |

## Notes
- [Any cross-cutting concerns, risks, or open questions]
```

---

## Phase Document Template

```markdown
# Phase [XX]: [Title]

## §1 Goal
[One sentence: what this phase delivers. Nothing beyond scope.]

## §2 Dependencies
- **Prerequisite phases**: [Phase IDs that must be `[x] Done`]
- **Source files to read**: [List file paths the agent must load before starting]

## §3 Design & Constraints
- **Architecture principles**: [e.g., dependency inversion, no circular imports]
- **Boundary conditions**: [Explicit failure scenarios to handle]
- **Out of scope**: [What this phase explicitly does NOT do]

## §4 Interface Contract
[Public APIs this phase will create or modify — signature-level detail]

```python
# Example
class UserService:
    def create_user(self, data: CreateUserDTO) -> User: ...
    def get_user(self, user_id: str) -> User | None: ...
```

## §5 Implementation Steps
1. [Concrete step with file path and action]
2. [Concrete step]
3. ...

## §6 Acceptance Criteria
- [ ] Tests written at `tests/...`
- [ ] Command `[test/build CLI command]` passes
- [ ] Linter/formatter check passes
- [ ] [Any additional criteria]

## §7 State Teardown Checklist
- [ ] `changelog.md` updated
- [ ] `api_registry/` index updated
- [ ] `master_overview.md` phase status set to `[x] Done`
```

---

## Changelog Template

```markdown
# Changelog — [Task Name]

## [Date] — Phase [XX]: [Title]

### Delivered
- [What was implemented]

### Decisions
- [Key design decisions and rationale]

### Deferred
- [Items discovered but intentionally not addressed]

---

*(Append new entries above this line)*
```

---

## API Registry Template

Each module gets its own file in `api_registry/`:

```markdown
# API Registry — [Module Name]

| Interface | File Path | Added in Phase |
|-----------|-----------|----------------|
| `UserService.create_user` | `src/services/user.py` | Phase 01 |
| `UserService.get_user` | `src/services/user.py` | Phase 01 |
| `UserRepository` | `src/repos/user.py` | Phase 02 |
```

Keep entries minimal: name + path + origin phase. Full signatures belong in the source code, not here.
