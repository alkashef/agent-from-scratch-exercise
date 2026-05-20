# todo-mcp-host

A minimal Python proof-of-concept MCP host for the existing CSV Todo MCP server.

A user types a task in natural language. The host fetches available tools from the MCP server, passes them to a local Ollama LLM, and the LLM decides which tool to call and with what arguments — exactly how real MCP hosts work. The host then executes that tool call via the official MCP Python SDK.

### The MCP/LLM tool-use pattern

1. **Host fetches tools** — `McpClient.list_tools()` connects to the MCP server and retrieves the available tool definitions (name, description, input schema).
2. **Host presents tools to the LLM** — `LlmClient.generate()` sends the user message and the tool definitions to Ollama using the function-calling API.
3. **LLM decides which tool to call** — the model responds with a structured `tool_call` (tool name + arguments) instead of free text.
4. **Host validates arguments** — `TaskParser.validate()` checks required fields and applies defaults.
5. **Host executes the tool via MCP** — `McpClient.call_tool()` calls the chosen tool on the MCP server using MCP protocol semantics.

The LLM never contacts the MCP server directly — it only decides what to call.

---

## PoC Scope

- Language: Python
- Platform: Windows (conda env)
- UI: Streamlit
- LLM runtime: Ollama (`qwen2.5:1.5b-instruct`)
- Transport: HTTP
- Role: MCP host/client only — connects to an existing MCP server
- Tool: `add_task` on the CSV Todo MCP server

Not included: task listing, editing, deletion, auth, cloud deployment, Docker.

---

## Architecture

```
User
  ↓
Streamlit Chat UI  (chat_ui.py)
  ↓
App  (main.py)
  ↓
LlmClient  (llm_client.py)   →   TaskParser  (task_parser.py)
  ↓
McpClient  (mcp_client.py)
  ↓
CSV Todo MCP Server  →  add_task tool
```

| File | Responsibility |
|------|---------------|
| `main.py` | `App` class — wires dependencies, drives the loop |
| `src/mcp_todo_host/chat_ui.py` | Streamlit adapter: `read_msg()` / `write_msg()` |
| `src/mcp_todo_host/llm_client.py` | Ollama wrapper — passes tools to LLM, returns tool call |
| `src/mcp_todo_host/task_parser.py` | Validates tool call arguments, applies defaults |
| `src/mcp_todo_host/mcp_client.py` | MCP HTTP client — lists tools and calls them |
| `src/mcp_todo_host/config.py` | Loads `config/.env` into a `Config` dataclass |
| `src/mcp_todo_host/logging_config.py` | Sets up file + console logging |

---

## Prerequisites

- Windows 10/11
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda
- [Ollama for Windows](https://ollama.com/download/windows)
- The existing CSV Todo MCP server running at `http://127.0.0.1:8000/mcp`

---

## Setup

### 1. Create and activate the conda environment

```powershell
conda create -n todo-mcp-host python=3.12 -y
conda activate todo-mcp-host
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install and start Ollama

Ollama is a native application — it is **not** installed via `requirements.txt`.

Download and install it from: https://ollama.com/download/windows

After installation, Ollama runs as a background service automatically. Verify it is running:

```powershell
ollama list
```

### 4. Pull the model

```powershell
ollama pull qwen2.5:1.5b-instruct
```

Verify the model is available:

```powershell
ollama list
```

### 5. Configure `config/.env`

The file already exists with sensible defaults:

```env
MCP_SERVER_URL=http://127.0.0.1:8000/mcp
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:1.5b-instruct
LLM_SYSTEM_PROMPT_PATH=prompts/system_prompt.md
LOG_LEVEL=INFO
LOG_FILE=./logs/host.log
```

Change `MCP_SERVER_URL` if your CSV Todo MCP server runs on a different address.

### 6. Verify `prompts/system_prompt.md`

This file instructs the LLM to use the provided tools to add tasks. Edit it only if you need to tune the model's behaviour.

---

## Run the app

Start the CSV Todo MCP server first (see its README), then:

```powershell
conda activate todo-mcp-host
streamlit run main.py
```

Open `http://localhost:8501` in a browser.

---

## Connect to the MCP server

The host connects to:

```
http://127.0.0.1:8000/mcp
```

using the MCP Streamable HTTP transport. It calls only the `add_task` tool.

---

## Example interaction

**User types:**

```
Buy milk for the team by Friday
```

**LLM tool call** (decided by the model after seeing the available tools):

```json
{"name": "add_task", "arguments": {"description": "Buy milk for the team", "status": "todo", "category": "", "people": "", "deadline": "Friday"}}
```

**MCP execution:** `add_task` called with the arguments above via MCP protocol.

**MCP server response:**

```json
{"success": true, "timestamp": "2026-05-19T10:00:00.000000+00:00", "csv_path": "./data/todo.csv"}
```

**UI shows:**

```
Task added: Buy milk for the team (saved at ./data/todo.csv)
```
