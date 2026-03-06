# GEMINI.md - Lumina Project Context

## Project Overview
Lumina is an interactive AI desktop pet agent that combines LLM reasoning with a Godot-rendered companion. It uses a Client-Server architecture where a Python backend (the brain) communicates with a Godot frontend (the body) via WebSockets.

### Key Components:
- **Server (Python/FastAPI)**: Handles ReAct agent logic, LLM integration, tool execution (file system, input simulation), and vision tasks (screenshots, OCR).
- **Client (Godot 4.4)**: Manages the visual desktop pet, animation state machines, transparent window overlay, and dialogue UI.

---

## Technical Stack
- **Backend**: Python 3.11+, `uv` (package manager), FastAPI, `websockets`, `mss` (screen capture), `paddleocr` (OCR), `pyautogui` (input simulation).
- **Frontend**: Godot 4.4 (GDScript), rendering with `gl_compatibility`, supports per-pixel transparency and "always on top" window mode.
- **Communication**: Local WebSocket (JSON-based protocol).

---

## Development Workflow
This project follows a document-driven development process using **task-architect**.
- **Task Tracking**: `docs/tasks/lumina/master_overview.md` contains the phase map and current status.
- **Phase Details**: `docs/tasks/lumina/stages/` contains detailed design and implementation plans for each phase.

### Building and Running
#### Server (Python)
```bash
cd server
uv sync                              # Install dependencies
uv run uvicorn lumina.main:app --reload   # Start development server
```
- **Health Check**: `http://127.0.0.1:8000/health`
- **Tests**: `uv run pytest` (from the `server` directory)

#### Client (Godot)
1. Open Godot Engine 4.4+.
2. Import the project from the `client/` directory.
3. Run the main scene (`res://scenes/main.tscn`) using F5.

---

## Project Structure
- `server/`: Python backend source and tests.
- `client/`: Godot project files, scenes, and GDScript logic.
- `docs/tasks/lumina/`: Comprehensive roadmap and stage-by-stage documentation.
- `PRD.md`: Detailed Product Requirement Document.

---

## Coding Conventions
- **Backend**: Use `async/await` for all I/O and communication tasks. Follow Ruff linting rules (line length 100).
- **Frontend**: Use GDScript 2.0. Window is configured for transparency and click-through (dynamic).
- **Protocol**: WebSocket messages should be JSON-serialized and versioned.

---

## Current Status
- **Stage**: Stage 1: Foundation Infrastructure (V0.1).
- **Current Phase**: Phase 01: Scaffolding and Environment Setup (Pending).
- Refer to `docs/tasks/lumina/master_overview.md` for the latest updates.
