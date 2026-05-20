# Execution Plan: CSV Todo MCP Server

## Overview

Build a minimal Python PoC MCP server for Windows that exposes one tool (`add_task`) over HTTP, appending task records to a local CSV file. Follow TDD: write tests first, implement to pass them, then document.

---

## Step 1 — Project Scaffold

Create the foundational files before writing any logic.

**Files to create:**

- `.gitignore` — Python standard ignores plus `venv/`, `data/`, `config/.env`
- `requirements.txt` — declare `mcp`, `pytest`, `python-dotenv`, `httpx`
- `config/.env` — runtime configuration:
  ```env
  TODO_CSV_PATH=./data/todo.csv
  MCP_HOST=127.0.0.1
  MCP_PORT=8000
  LOG_LEVEL=INFO
  LOG_FILE=./logs/server.log
  ```
- `src/csv_todo_mcp/__init__.py` — empty package marker

**Goal:** `pip install -r requirements.txt` succeeds and the package is importable.

---

## Step 2 — Configuration Module

**File:** `src/csv_todo_mcp/config.py`

- Use `python-dotenv` to load `config/.env`
- Expose a `Config` dataclass with fields: `csv_path: str`, `host: str`, `port: int`, `log_level: str`, `log_file: str`
- `log_level` and `log_file` are optional in `.env`; defaults are `"INFO"` and `"./logs/server.log"`
- Provide a `load_config(env_path: str) -> Config` factory function
- No global state — callers instantiate `Config` explicitly

**Goal:** `Config` can be constructed from the `.env` file and passed through the call stack.

---

## Step 3 — CSV Repository

**File:** `src/csv_todo_mcp/csv_repository.py`

- Class: `CsvRepository(csv_path: str)`
- Method: `append_task(description: str, status: str = "todo", category: str = "", people: str = "", deadline: str = "") -> dict`
  - Creates the file and parent directories on first write
  - Writes CSV header (`timestamp,description,status,category,people,deadline`) exactly once
  - Appends one row without overwriting existing rows
  - Generates `timestamp` as a UTC ISO-8601 string at the moment of the call
  - Returns `{"timestamp": ..., "description": ..., "status": ..., "category": ..., "people": ..., "deadline": ..., "csv_path": ...}`
- Use Python's standard `csv` module — no pandas

**Goal:** Multiple `append_task` calls produce a well-formed CSV with one header and N data rows.

---

## Step 4 — Tool Handler

**File:** `src/csv_todo_mcp/tool_handlers.py`

- Function: `add_task_handler(args: dict, repo: CsvRepository) -> dict`
  - Validates that `description` is present and non-empty; raises `ValueError` if missing
  - Reads optional `status` (default `"todo"`), `category` (default `""`), `people` (default `""`), `deadline` (default `""`) from `args`
  - Delegates to `repo.append_task()`
  - Returns MCP tool result: `{"success": True, "timestamp": ..., "csv_path": ...}`
- On `ValueError`, return `{"success": False, "error": "<message>"}`

**Goal:** Handler is pure and testable in isolation — no I/O beyond what `CsvRepository` does.

---

## Step 5 — MCP Server

**File:** `src/csv_todo_mcp/server.py`

- Use `FastMCP` from the official MCP Python SDK
- Register the `add_task` tool with schema:
  - `description`: string, required
  - `status`: string, optional, default `"todo"`
  - `category`: string, optional
  - `people`: string, optional
  - `deadline`: string, optional
- Wire tool invocation to `add_task_handler`, passing a `CsvRepository` instance
- Accept `config: Config` as a parameter — no hardcoded paths or ports
- Entry point: `run_server(config: Config)` starts the HTTP server on `config.host:config.port`
- Module-level `if __name__ == "__main__"` block calls `run_server(load_config(...))`

**Goal:** `python -m csv_todo_mcp.server` starts a running MCP server discoverable by clients.

---

## Step 6 — End-to-End Tests

**File:** `tests/test_mcp_server_e2e.py`

> Write these tests **before** implementing Steps 2–5. Run them and confirm expected failures. Then implement until all pass.

**Fixtures:**
- `tmp_csv_path` — a `tmp_path`-scoped CSV path; never the real configured file
- `running_server` — starts the server as a subprocess against `tmp_csv_path`, polls the health/ready endpoint, yields, then terminates cleanly; no `time.sleep()` with arbitrary delays

**Tests:**

| # | Test | Assertion |
|---|------|-----------|
| 1 | Server starts | Process is alive after startup |
| 2 | Session initialization | MCP client handshake succeeds |
| 3 | Tool discovery | `tools/list` response includes `add_task` with correct input schema |
| 4 | Tool invocation | `tools/call add_task {description: "Buy milk"}` returns `success: true` and creates CSV with 1 data row |
| 5 | Idempotent append | Second `tools/call` appends row 2; CSV has 2 data rows, header appears once |
| 6 | Missing description error | `tools/call add_task {}` returns a structured error, CSV unchanged |

**Rules:**
- Use `httpx` (sync or async) or the MCP SDK client — no raw socket calls
- All file I/O uses `tmp_path` fixtures
- No `time.sleep()` — poll with timeout instead

**Goal:** `pytest tests/` passes green with all 6 tests.

---

## Step 7 — Logging

**Files:** `src/csv_todo_mcp/server.py`, `src/csv_todo_mcp/tool_handlers.py`

- Add `_configure_logging(config: Config) -> logging.Logger` in `server.py`
  - Attaches a `StreamHandler` (stdout) and `FileHandler` (auto-creates parent dirs) to the `"csv_todo_mcp"` logger
  - Both handlers use the format: `%(asctime)s %(levelname)-8s %(name)s — %(message)s`
- In `run_server()`: call `_configure_logging` first, log startup, wrap `mcp.run()` in `try/finally` to log shutdown
- In `tool_handlers.py`: add `logger = logging.getLogger(__name__)` and log at three points:
  - ERROR before raising a validation error
  - INFO on tool entry (description, status)
  - INFO on successful append (csv_path, timestamp)

**Goal:** Console and file both receive structured plain-text log lines for every meaningful event.

---

## Step 8 — README

**File:** `README.md`

Sections to include:

1. **Purpose** — one-paragraph description of what this PoC does
2. **Scope** — what is and is not included (link to CLAUDE.md for full constraints)
3. **Prerequisites** — Python 3.11+, Windows
4. **Setup**
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Configuration** — document `config/.env` variables
6. **Run tests** — `pytest tests/`
7. **Run the server** — `python -m csv_todo_mcp.server`
8. **MCP tool reference** — `add_task` schema and example call
9. **Expected CSV output** — column names and sample rows

**Goal:** A new developer can set up and run the project from README alone.

---

## Implementation Order (TDD)

```
Step 6 (write tests — all fail)
  → Step 1 (scaffold)
  → Step 2 (config)
  → Step 3 (CSV repo)
  → Step 4 (tool handler)
  → Step 5 (MCP server)
  → run tests — all pass
Step 7 (logging)
Step 8 (README)
```

Never skip ahead. Each step should produce a passing test before the next step begins.

---

## Definition of Done

- [x] `pytest tests/` passes with 0 failures
- [x] `python -m csv_todo_mcp.server` starts without error
- [x] An MCP client can call `add_task` and observe a CSV row written to disk
- [x] `README.md` covers setup-to-run without gaps
- [x] No global variables, no pandas, no hardcoded paths
- [x] Logging to console and file for startup, tool calls, results, and errors
