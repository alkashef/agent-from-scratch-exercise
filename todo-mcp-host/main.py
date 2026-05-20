"""Entry point — App class wires dependencies and drives the Streamlit loop."""

import logging

from src.mcp_todo_host.config import Config
from src.mcp_todo_host.llm_client import LlmClient
from src.mcp_todo_host.logging_config import setup_logging
from src.mcp_todo_host.mcp_client import McpClient
from src.mcp_todo_host.task_parser import TaskParser

logger = logging.getLogger(__name__)


class App:
    """Orchestrates the UI, LLM client, task parser, and MCP client.

    Owns config and all service dependencies. Each call to run() handles
    one UI interaction (read one message, write one response).
    """

    def __init__(self, config: Config, llm_client: LlmClient, task_parser: TaskParser,
                 mcp_client: McpClient, ui) -> None:
        """Initialise the App with all wired dependencies.

        Args:
            config: Application configuration.
            llm_client: LlmClient instance.
            task_parser: TaskParser instance.
            mcp_client: McpClient instance.
            ui: ChatUI instance exposing read_msg() and write_msg().
        """
        self._config = config
        self._llm = llm_client
        self._parser = task_parser
        self._mcp = mcp_client
        self._ui = ui

    def process(self, user_message: str) -> str:
        """Run the full MCP/LLM tool-use loop for a single user message.

        This is the core of the application. It implements the standard pattern
        used by real MCP hosts:

        Step 1 — Discover tools
            Ask the MCP server which tools are available. The server returns
            each tool's name, description, and input schema. This is how the
            host (and the LLM) learn what actions exist without any hardcoding.

        Step 2 — Present tools to the LLM
            Send the user message together with the tool definitions to the
            local Ollama model. The model sees both the user's intent and the
            available tools, and responds with a structured tool_call (tool
            name + arguments) instead of free text.

        Step 3 — Validate the tool call arguments
            Check that the LLM-produced arguments are usable: description must
            be present and non-empty. Apply defaults for optional fields.

        Step 4 — Execute the tool via MCP
            Forward the tool name and validated arguments to the MCP server
            using MCP protocol semantics (not ad-hoc REST). The server runs
            the tool and returns a result.

        Step 5 — Return a human-readable response
            Format the result into a short success string for the UI.

        Args:
            user_message: Raw text from the user.

        Returns:
            Human-readable success string including the task description.

        Raises:
            ValueError: If the LLM does not invoke a tool or arguments are invalid.
            ConnectionError: If the MCP server or Ollama is unreachable.
        """
        # ******************************* START HERE *******************************
        #
        # You need to implement the 4-step agent loop described above.
        # Each step maps to a method call on one of the injected dependencies.
        #
        # Step 1 — fetch the list of available tools from the MCP server
        #   Call:  self._mcp.list_tools()
        #   Returns: a list of tool definition dicts (name, description, schema)
        #
        # Step 2 — send the user message AND the tools to the LLM
        #   Call:  self._llm.generate(user_message, tools)
        #   Returns: {"name": "add_task", "arguments": {"description": ..., ...}}
        #
        # Step 3 — validate the arguments the LLM produced
        #   Call:  self._parser.validate(tool_call["arguments"])
        #   Returns: a clean dict with all 5 required keys
        #   Also log the args: logger.info("Parsed task arguments: %s", args)
        #
        # Step 4 — execute the tool on the MCP server
        #   Call:  self._mcp.call_tool(tool_call["name"], args)
        #   Returns: {"success": True, "timestamp": "...", "csv_path": "..."}
        #
        # Step 5 — return a success message to display in the chat UI
        #   Example: f"Task added: {args['description']} (saved at {result.get('csv_path', '?')})"
        #
        raise NotImplementedError("Implement the agent loop here")
        # ******************************** END HERE ********************************

    def run(self) -> None:
        """Read one user message from the UI and write the response.

        Does nothing if read_msg returns None (no pending input).
        Catches all exceptions and writes an 'Error: ...' string to the UI.
        """
        user_message = self._ui.read_msg()
        if user_message is None:
            return
        logger.info("Processing user message: %s", user_message)
        try:
            response = self.process(user_message)
        except Exception as exc:
            logger.error("Error processing message: %s", exc)
            response = f"Error: {exc}"
        self._ui.write_msg(response)


def main() -> None:
    """Load configuration, wire all dependencies, and run the app."""
    from src.mcp_todo_host.chat_ui import ChatUI
    config = Config.from_env()
    setup_logging(config)
    logger.info("Starting MCP host. Server: %s, Model: %s",
                config.mcp_server_url, config.ollama_model)
    App(config, LlmClient(config), TaskParser(), McpClient(config), ChatUI(config)).run()


if __name__ == "__main__":
    main()
