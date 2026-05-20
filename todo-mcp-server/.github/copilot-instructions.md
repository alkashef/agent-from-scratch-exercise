# `.github/copilot-instructions.md`

## Project Objective

Build a minimal Python proof-of-concept MCP server for Windows that exposes one MCP tool over HTTP.

The tool writes one task record into a CSV-based to-do list stored as a file on disk.

This is a PoC, not a production system. Prefer simplicity, clarity, and protocol correctness over scalability, extensibility, or enterprise hardening.

---

## Non-Negotiable Scope

* Language: Python.
* Platform: Windows only.
* Transport: HTTP using MCP-compatible Streamable HTTP behavior.
* Server type: MCP server.
* Tool count: exactly one MCP tool.
* Tool behavior: append one task record to a CSV file on disk.
* Storage: local CSV file only.
* Testing approach: write end-to-end tests before implementation.
* Protocol: conform to the MCP protocol and use the official MCP Python SDK where practical.

Do not add extra features unless explicitly requested.

---

## Required Project Files

The project must include:

```text
README.md
requirements.txt
.gitignore
config/.env
```

Recommended minimal structure:

```text
.
├── .github/
│   └── copilot-instructions.md
├── config/
│   └── .env
├── src/
│   └── csv_todo_mcp/
│       ├── __init__.py
│       ├── config.py
│       ├── csv_repository.py
│       ├── server.py
│       └── tool_handlers.py
├── tests/
│   └── test_mcp_server_e2e.py
├── README.md
├── requirements.txt
└── .gitignore
```

Keep this structure minimal. Do not introduce additional folders unless they remove duplication or improve clarity.

---

## Development Workflow

Follow this order strictly:

1. Write end-to-end tests first.
2. Run tests and confirm they fail for the expected reason.
3. Implement the smallest code needed to pass the tests.
4. Refactor only after tests pass.
5. Update README only after behavior is implemented and tested.

Do not implement production-grade abstractions before the PoC works end to end.

---

## MCP Requirements

Use MCP protocol concepts correctly:

* The server must expose tools through MCP, not through an ad-hoc REST endpoint.
* The HTTP transport must be MCP-compatible.
* The client/test flow must validate MCP initialization and tool invocation behavior.
* The exposed tool must have a clear input schema.
* The tool result must be structured and predictable.

Expected MCP tool:

```text
tool name: add_task
purpose: append one task record to the configured CSV to-do file
```

Recommended tool input fields:

```text
title: string, required
description: string, optional
status: string, optional, default "todo"
```

Recommended CSV columns:

```text
id,title,description,status,created_at
```

Use deterministic logic for CSV writing. Do not use an LLM anywhere in the server implementation.

---

## Configuration Rules

Use `config/.env` for runtime configuration.

Recommended values:

```env
TODO_CSV_PATH=./data/todo.csv
MCP_HOST=127.0.0.1
MCP_PORT=8000
```

Rules:

* Do not hardcode file paths in business logic.
* Load configuration in one place only.
* Pass configuration through class attributes or function parameters.
* Do not use global mutable state.
* Do not commit secrets if any are later introduced.

---

## Coding Standards

### Minimality

Write the smallest clear implementation that satisfies the tests and requirements.

Avoid:

* unnecessary frameworks
* unnecessary classes
* dependency injection frameworks
* background workers
* databases
* authentication
* authorization
* Docker
* cloud deployment
* telemetry
* caching
* complex logging infrastructure

### No Global Variables

No global variables are allowed.

All state must be passed through:

* function arguments
* class constructor arguments
* class attributes

Constants are acceptable only if they are immutable and genuinely constant.

### No Code Duplication

No code duplication is allowed.

Each piece of logic must exist in exactly one place.

If two modules need the same behavior, one module must call the other. Never copy logic between files.

### Docstrings

Every class and method must have a docstring.

Class docstrings must describe:

* the module's responsibility
* what state the class owns, if any

Method docstrings must describe:

* what the method does
* parameters
* return value

Use concise docstrings. Do not write verbose documentation inside code.

---

## Testing Standards

Write end-to-end tests first.

E2E tests should verify:

* the MCP server starts successfully
* the MCP client can initialize a session
* the `add_task` tool is discoverable
* invoking `add_task` appends exactly one row to the CSV file
* the written CSV row contains expected values
* repeated tool calls append multiple rows without overwriting previous rows

Use temporary test files and directories.

Tests must not write to the real configured CSV file.

Avoid brittle sleeps. Use deterministic startup and teardown patterns where possible.

---

## CSV Behavior

The CSV repository must:

* create the CSV file if it does not exist
* create parent directories if needed
* write the header exactly once
* append new task rows without overwriting existing rows
* generate deterministic row structure
* preserve existing rows

Do not use pandas. Use Python's standard `csv` module unless a stronger reason exists.

---

## Error Handling

Keep error handling minimal but explicit.

Handle:

* missing required task title
* invalid CSV path
* file write errors
* malformed tool input

Errors should be readable and testable.

Do not swallow exceptions silently.

---

## README Requirements

`README.md` must include:

* project purpose
* PoC scope
* prerequisites
* Windows setup steps
* how to install dependencies
* how to configure `config/.env`
* how to run tests
* how to run the MCP server
* what the MCP tool does
* expected CSV output format

Keep the README practical and short.

---

## Dependency Rules

Use the fewest dependencies possible.

Expected dependency categories:

* official MCP Python SDK
* test framework, preferably `pytest`
* dotenv loader, if needed
* HTTP/server dependencies only if required by the MCP SDK transport path

Do not add libraries for problems solved cleanly by the Python standard library.

---

## What Not to Build

Do not build:

* a UI
* a REST API separate from MCP
* a database layer
* authentication
* user accounts
* task editing
* task deletion
* task listing unless required for tests
* scheduling
* cloud deployment
* Docker setup
* multiple MCP tools
* agent logic
* LLM calls
* production observability

---

## Copilot Behavior Rules

When generating code:

* Prefer simple, readable Python.
* Preserve the locked scope.
* Write tests before implementation.
* Keep files short and cohesive.
* Ask before making architectural changes.
* Do not introduce new dependencies without explaining why.
* Do not duplicate logic.
* Do not use globals.
* Add required docstrings.
* Make every change directly support the PoC objective.

When uncertain:

* choose the simpler implementation
* preserve MCP protocol correctness
* avoid production-grade expansion
* leave a clear TODO only if the issue is outside the PoC scope
