# Task Architect — Document Templates

## Master Overview Template

```markdown
# Task: [Task Name]

## Meta
- **Created**: [date]
- **Last Updated**: [date]
- **Status**: In Progress | Completed | Blocked
- **Complexity**: Moderate | High

## Objective
[1–2 sentences describing the overall goal and deliverable]

## References & Knowledge Base
- **External Docs**: [e.g., OpenUSD Documentation - /path/to/docs]
- **Technical Specs**: [e.g., Schema Definition - /path/to/schema.json]
- **Research/Context**: [e.g., Design Doc - /path/to/design.md]

## Constraints & Architecture Decisions
- [Key constraint or decision 1]
- [Key constraint or decision 2]

## Phase Map

### Stage 1: [Label] *(omit stage grouping for moderate tasks)*

| Phase | Title | Status | File Path | Dependencies |
|-------|-------|--------|-----------|--------------|
| 01 | [Data Model] | [ ] Pending | `./phases/phase_01.md` | — |
| 02 | [Interfaces] | [ ] Pending | `./phases/phase_02.md` | Phase 01 |

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
- **Reference Materials**: 
    - [ ] [Path to Reference A (e.g. OpenUSD spec)]
    - [ ] [Path to Reference B]
- **Source files to read**: 
    - [ ] [List file paths to load]

## §3 Design & Constraints
- **Architecture principles**: [e.g., dependency inversion]
- **Boundary conditions**: [Explicit failure scenarios]
- **Out of scope**: [Explicitly NOT doing]

## §4 Interface Contract
[Public APIs this phase will create or modify — signature-level detail]

```python
# Example
class UserService:
    def create_user(self, data: CreateUserDTO) -> User: ...
```

## §5 Implementation Steps
1. [Concrete step with file path and action]
2. [Concrete step]

## §6 Acceptance Criteria
- [ ] Tests written at `tests/...`
- [ ] Command `[test/build CLI command]` passes
- [ ] Linter/formatter check passes

## §7 State Teardown Checklist
- [ ] **Phase Document Updated** (if design changed during implementation)
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

| Interface | File Path | Origin Phase (Link) | Usage Note |
|-----------|-----------|---------------------|------------|
| `UserService.create_user` | `src/services/user.py` | `../phases/phase_01.md` | Required DTO validation before call |
```
