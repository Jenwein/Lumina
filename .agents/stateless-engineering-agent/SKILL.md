---
name: stateless-engineering-agent
description: Transform AI into a stateless code executor based on an external state machine, strictly following SDD (Specification-Driven Development) and TDD (Test-Driven Development) for complex software engineering tasks. Use when starting or continuing work on a project where state must be strictly tracked across sessions.
---

# Stateless Engineering Agent (SDD-TDD-State-Machine)

This skill mandates transforming AI behavior into a state-driven executor that relies on an externalized memory architecture. It is designed to solve common AI issues like context drift, hallucination, and "hacking" by enforcing a strict state machine.

## Externalized Memory Architecture (.agent/)

Maintain a `.agent/` directory in the project root as the Single Source of Truth (SSOT).

- **STATE.md (Hot - Core Entrance)**: Mandatory first read in any session. Contains `CURRENT_TASK`, `STATUS`, and `RETRY_COUNT`. No code logic allowed.
- **ROADMAP.md (Warm - Macro Blueprint)**: Global progress tracker using Markdown checkboxes. Read/write only during phase transitions.
- **API_REGISTRY.md (Warm - Contract Center)**: SSOT for module interactions. Defines API signatures, memory ownership, and thread safety. MANDATORY SDD: Update before coding.
- **tasks/task_*.md (Ephemeral - Work Log)**: Detailed requirements, CoT reasoning, and error logs for the current task. Completed tasks are "Cold" and should not be read in new sessions.
- **ADR/ (Cold - Architectural Decisions)**: Long-term records of major technical choices and trade-offs.

## Core State Machine Workflow

Follow these states strictly based on `.agent/STATE.md`:

1.  **IDLE**: Get next task from `ROADMAP.md`, create `tasks/task_N.md`, set status to `DRAFT_SPEC`.
2.  **DRAFT_SPEC (SDD)**: Design interfaces and data structures. Update `API_REGISTRY.md`. Set status to `WRITE_TEST`.
3.  **WRITE_TEST (TDD)**: Write test cases in the project's test directory. Build must FAIL (Red). Set status to `IMPLEMENTING`.
4.  **IMPLEMENTING**: Write business logic (`.h`/`.cpp`). Iterate until tests pass (Green).
5.  **COMPLETE**: Update `ROADMAP.md`, mark task finished, reset status to `IDLE`.

## Strict Constraints

- **Anti-Hacking Limit**: Increment `RETRY_COUNT` on build/test failures. If `RETRY_COUNT > 3`, set status to `BLOCKED`, document failures in `task_N.md`, and **ABORT**. Await human intervention.
- **I/O Optimization**: Batch changes (e.g., both header and source) before triggering a build.
- **Test-Exempt Boundary**: For hardware/GUI-specific logic, mark `[Test-Exempt]` in `ROADMAP.md` and skip `WRITE_TEST`. Require manual verification.
- **Generalization vs. Overfitting**: Implementation must be generic business logic. Never hardcode values to pass specific test cases.

## Usage
- Refer to `assets/` for templates for the `.agent/` directory.
