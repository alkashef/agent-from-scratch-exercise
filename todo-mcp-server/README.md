# CSV Todo MCP Server

A minimal Python proof-of-concept MCP server that exposes one tool — `add_task` — over HTTP. Calling the tool appends a task record to a local CSV file.

## Scope

This is a PoC. It has one tool, one storage backend (CSV), and no auth, UI, or database. See [CLAUDE.md](CLAUDE.md) for the full constraints.

## Prerequisites

- Python 3.11+
- Windows

## Setup

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Configuration

Edit `config/.env` before running:

| Variable | Default | Description |
|---|---|---|
| `TODO_CSV_PATH` | `./data/todo.csv` | Path to the CSV file (created automatically) |
| `MCP_HOST` | `127.0.0.1` | Host the server binds to |
| `MCP_PORT` | `8000` | Port the server listens on |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LOG_FILE` | `./logs/server.log` | Path to the log file (created automatically) |

## Run the server

```
python -m csv_todo_mcp.server
```

To use a different config file:

```
python -m csv_todo_mcp.server --env-file path/to/.env
```

## Use with Claude Desktop

Claude Desktop only supports stdio-based MCP servers, so `mcp-remote` is used as a proxy that bridges it to the HTTP server. [Node.js](https://nodejs.org) must be installed.

**Config file location (Windows):**

```
%APPDATA%\Claude\claude_desktop_config.json
```

**Add this entry under `mcpServers`:**

```json
{
  "mcpServers": {
    "csv-todo": {
      "command": "npx",
      "args": ["mcp-remote", "http://127.0.0.1:8000/mcp"]
    }
  }
}
```

Adjust the port to match `MCP_PORT` in your `config/.env`.

**Steps:**

1. Start the server: `python -m csv_todo_mcp.server`
2. Edit `claude_desktop_config.json` as shown above.
3. Restart Claude Desktop.
4. Open a new conversation — Claude will have access to the `add_task` tool.

To verify the tool is available, ask Claude: *"What tools do you have?"* and confirm `add_task` appears.

## Logging

The server logs to both console and file using plain-text lines:

```
2026-05-19 10:00:00,123 INFO     csv_todo_mcp.server — Server starting on 127.0.0.1:8000 | csv=./data/todo.csv | log=./logs/server.log
2026-05-19 10:00:05,456 INFO     csv_todo_mcp.tool_handlers — add_task called: description='Buy milk' status='todo'
2026-05-19 10:00:05,460 INFO     csv_todo_mcp.tool_handlers — Task appended → ./data/todo.csv (at 2026-05-19T10:00:05.460000+00:00)
2026-05-19 10:00:10,789 ERROR    csv_todo_mcp.tool_handlers — add_task validation error: description is required and must be a non-empty string
2026-05-19 10:01:00,000 INFO     csv_todo_mcp.server — Server stopped
```

The log file path and level are controlled by `LOG_FILE` and `LOG_LEVEL` in `config/.env`.

## MCP tool reference

**Tool name:** `add_task`

**Purpose:** Append one task record to the configured CSV file.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `description` | string | yes | — | Human-readable task description |
| `status` | string | no | `todo` | Task status |
| `category` | string | no | `""` | Category label |
| `people` | string | no | `""` | Comma-separated people names |
| `deadline` | string | no | `""` | Deadline string |

**Result:**

```json
{
  "success": true,
  "timestamp": "2026-05-19T10:00:00.000000+00:00",
  "csv_path": "./data/todo.csv"
}
```

## Expected CSV output

```
timestamp,description,status,category,people,deadline
2026-05-19T10:00:00.000000+00:00,Buy milk,todo,,,
2026-05-19T10:01:00.000000+00:00,Write tests,done,dev,,2026-05-20
```
