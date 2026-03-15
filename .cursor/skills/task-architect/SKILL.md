# Task Architect & Execution Controller V2.2

A document-driven workflow that turns the AI into a **stateless executor** — combating context loss, hallucination, and scope creep by enforcing strict decomposition, phase isolation, and physical verification.

## Core Principle

**Never code before thinking.** Every complex task must pass through: Validate → Decompose → Execute (per-phase) → Teardown.

---

## Step 1: Requirement Validation & Reference Mapping

1. Assess clarity: Is the goal unambiguous? Are acceptance criteria defined?
2. **Identify References**: Map all provided documentation (e.g., OpenUSD documentation paths).

---

## Step 2: Decomposition & Scaffolding

### 2.2 Create Document Tree

```text
docs/tasks/<task_name>/
├── master_overview.md (Entry Point)
├── changelog.md
├── api_registry/
│   └── <module_name>.md
└── phases/
    ├── phase_01_<label>.md
    └── phase_02_<label>.md
```

### 2.3 Generate `master_overview.md` (SSOT)

- **Requirement**: The Phase Map **MUST** include relative file paths (e.g., `./phases/phase_01.md`).
- **Requirement**: All reference documents must be listed in the `References` section.

---

## Step 3: Phase Session Protocol (The "Reboot" Rule)

When starting a phase (especially in a new session):

1. **Read `master_overview.md`** — find the target phase.
2. **Read `changelog.md` (Last 5 Entries)** — **CRITICAL**: Understand recent architectural decisions and "traps" to avoid regressions.
3. **Read the target `phases/phase_XX.md`** — load goals and interface contracts.
4. **LOAD REFERENCES**: Immediately read all files/docs listed in `§2 Reference Materials`.
5. **Read Source Files**: Load existing code listed in `§2 Source files to read`.

---

## Step 4: TDD Execution Loop
(Write failing test → Run → Implement → Run → Lint)

---

## Step 5: Phase Completion Gate (MANDATORY)

**⚠ This step is NON-OPTIONAL. You MUST NOT move to the next phase, end the session, or declare the phase "done" until every item below is completed.**

### 5.1 Verify Acceptance Criteria (§6)

Go through **every** item in the phase's `§6 Acceptance Criteria` list. For each item:

1. **Execute the verification** — run the test command, manually verify the behavior, or check the condition described.
2. **Mark the checkbox** `[x]` in the phase document only after you have **physically verified** it passes.
3. If any item fails: fix the issue first, re-run, then check the box.
4. **All boxes must be `[x]`** before proceeding to §7.

### 5.2 Execute Teardown Checklist (§7)

Go through **every** item in the phase's `§7 State Teardown Checklist`. These items are **concrete file-editing actions**, not suggestions:

1. **Update Phase Document** — If any design changed during implementation (interface signatures, file paths, architecture), update §3/§4/§5 to reflect the **truth** of the final code. The phase doc must always match reality.
2. **Update `changelog.md`** — Append a new entry with Delivered/Decisions/Deferred sections. This is the project's memory.
3. **Update `api_registry/`** — Add or update every new/changed public interface. Each entry MUST include:
   - Link back to the phase file
   - Usage note explaining calling pattern or constraints
4. **Update `master_overview.md`** — Change the phase status from `[ ] Pending` to `[x] Done`.
5. **Mark each §7 checkbox** `[x]` in the phase document after completing the action.

### 5.3 Self-Verification Prompt

After completing all items, ask yourself:
- "If a new AI session starts tomorrow with zero context, can it read these docs and understand exactly what was built, how it works, and what decisions were made?"
- If the answer is no, the teardown is incomplete.

---

## Guardrail Rules (V2.2)

- **History Awareness**: Never start a phase without reading the `changelog`'s recent entries.
- **Entry Point Navigation**: Always start from `master_overview.md`.
- **Reference Persistence**: Explicitly link and re-read reference docs in every phase.
- **No skipping Teardown**: The documentation is the project's brain. **Skipping §6/§7 is the single most common failure mode** — treat them as part of the implementation, not an afterthought.
- **Checkbox Discipline**: A checkbox `[ ]` means "not done". A checkbox `[x]` means "I have physically verified this". Never check a box you haven't verified.
- **Phase Gate**: You cannot mark a phase `[x] Done` in `master_overview.md` until all §6 and §7 checkboxes are `[x]`.

---

## Templates

See [templates.md](templates.md) for updated Master Overview, Phase Document, and **Enhanced API Registry** structures.
