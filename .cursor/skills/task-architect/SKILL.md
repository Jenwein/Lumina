---
name: task-architect
description: Architect and manage complex development tasks through document-driven decomposition, state-machine workflows, and strict phase isolation. Use when the user starts a complex feature, epic, or multi-phase project, asks to begin staged development, or provides a large or ambiguous requirement that needs structured breakdown before coding.
---

# Task Architect & Execution Controller

A document-driven workflow that turns the AI into a **stateless executor** — combating context loss, hallucination, and scope creep in large projects by enforcing strict decomposition, phase isolation, and physical verification.

## Core Principle

**Never code before thinking.** Every complex task must pass through: Validate → Decompose → Execute (per-phase) → Teardown.

---

## Step 1: Requirement Validation & Guardrails

On receiving a task, **stop — do not write code**.

1. Assess clarity: Is the goal unambiguous? Are acceptance criteria defined?
2. Check architecture: Does it violate SOLID, separation of concerns, or existing project conventions?
3. Check dependencies: Are external services, schemas, or APIs clearly specified?

**If any issue is found**, present the user with 2–3 concrete options (A / B / C) with trade-off analysis. Only proceed after explicit user confirmation.

Use the AskQuestion tool when available for structured option presentation.

---

## Step 2: Decomposition & Scaffolding

### 2.1 Complexity Assessment

| Complexity | Structure |
|---|---|
| Moderate (3–6 phases) | Task → Phases |
| High (7+ phases or cross-cutting) | Task → Stages → Phases |

### 2.2 Create Document Tree

Create the following structure at the project root:

```text
docs/tasks/<task_name>/
├── master_overview.md
├── changelog.md
├── api_registry/
│   └── <module_name>.md
└── stages/                    # only if multi-stage
    ├── stage_01_<label>/
    │   ├── phase_01_<label>.md
    │   └── phase_02_<label>.md
    └── stage_02_<label>/...
```

For moderate tasks without stages, place phase files directly:

```text
docs/tasks/<task_name>/
├── master_overview.md
├── changelog.md
├── api_registry/
│   └── <module_name>.md
├── phase_01_<label>.md
└── phase_02_<label>.md
```

### 2.3 Generate `master_overview.md`

Use the master overview template from [templates.md](templates.md). This file is the **Single Source of Truth (SSOT)** — it tracks every phase's status and must be updated at the end of each phase.

### 2.4 Generate Phase Documents

For each phase, generate a `phase_XX_<label>.md` using the phase template from [templates.md](templates.md). Each phase document must be self-contained: an agent reading only `master_overview.md` + the phase doc should have enough context to execute.

---

## Step 3: Phase Session Protocol

When the user says "Execute Phase X" (or similar):

1. **Read** `master_overview.md` — verify the phase's prerequisites are met (all dependencies marked `[x] Done`).
2. **Read** the target `phase_XX.md` — load goal, constraints, interface contracts, and implementation steps.
3. **Read** relevant files listed in the phase's `§2 Dependencies` section.
4. If starting a new conversation/session, instruct the user:
   > "Please start a new session with the prompt: **Execute `<task_name>` Phase X**"

This ensures context is rebuilt from documents, not from stale conversation memory.

---

## Step 4: TDD Execution Loop

Within a phase, follow this strict cycle:

```
Write failing test → Run test (confirm failure) → Implement → Run test (confirm pass) → Lint check
```

- **Physical execution is mandatory** — never assume a test passes; run it.
- Stay within the phase's declared scope. If you discover work outside scope, note it in `changelog.md` as a future task and do NOT implement it now.

---

## Step 5: State Teardown & Context Unload

After a phase's acceptance criteria are all met:

1. **Update `api_registry/`** — add new public interfaces (file path + function/class name only, not full signatures) to the appropriate module file.
2. **Append to `changelog.md`** — record what was delivered, key decisions made, and any deferred items.
3. **Update `master_overview.md`** — mark the phase `[x] Done`, update timestamp.
4. **Report** to the user: phase status, next recommended phase, any blockers.

---

## Guardrail Rules

These rules apply at ALL times during task execution:

- **No skipping steps.** The state machine is: Validate → Decompose → (Execute → Teardown) per phase.
- **No scope creep.** If implementation reveals new needs, log them — don't implement them in the current phase.
- **No hallucinated passes.** Every test and lint check must be physically executed.
- **Documents are the source of truth.** When in doubt, re-read the docs, don't rely on conversation context.
- **One phase at a time.** Complete teardown before starting the next phase.

---

## Quick Reference

| Action | Command/File |
|---|---|
| Start new task | "Architect task: \<description\>" |
| Execute a phase | "Execute \<task\> Phase X" |
| Check status | Read `docs/tasks/<task>/master_overview.md` |
| Review changes | Read `docs/tasks/<task>/changelog.md` |
| Find an API | Read `docs/tasks/<task>/api_registry/<module>.md` |

## Templates

For all document templates (master overview, phase, changelog, api registry), see [templates.md](templates.md).
