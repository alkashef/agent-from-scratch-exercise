"""MCP HTTP client — lists tools and calls them on the CSV Todo MCP server."""

import asyncio
import json
import logging

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from src.mcp_todo_host.config import Config

logger = logging.getLogger(__name__)


def _mcp_tool_to_ollama(tool) -> dict:
    """Convert an MCP Tool object to Ollama function-calling format.

    The MCP SDK returns Tool objects with attributes: name, description,
    and inputSchema (a JSON Schema dict describing the tool's parameters).

    The Ollama chat API expects tools in a different shape. This function
    bridges the two formats so the LLM can understand what tools exist.

    Args:
        tool: MCP Tool object with .name, .description, and .inputSchema.

    Returns:
        Dict in Ollama function-calling format:
        {
            "type": "function",
            "function": {
                "name":        <str>,
                "description": <str>,
                "parameters":  <JSON Schema dict>,
            },
        }
    """
    # ******************************* START HERE *******************************
    #
    # Build and return the Ollama-format dict from the MCP Tool object's attributes.
    # Use tool.description or "" to avoid passing None as the description.
    #
    raise NotImplementedError("Convert the MCP Tool object to Ollama format")
    # ******************************** END HERE ********************************


class McpClient:
    """Lists tools and calls them on the CSV Todo MCP server via HTTP transport.

    Owns the MCP server URL. Each method opens a fresh HTTP connection and
    closes it on completion — there is no persistent connection.

    The MCP SDK is async-first (uses async/await). The public methods
    list_tools() and call_tool() are synchronous wrappers that use
    asyncio.run() to drive the async internals from synchronous caller code.
    """

    def __init__(self, config: Config) -> None:
        """Initialise the MCP client.

        Args:
            config: Application configuration.
        """
        self._url = config.mcp_server_url

    def list_tools(self) -> list[dict]:
        """Fetch available tools from the MCP server in Ollama function format.

        Opens a connection to the MCP server, retrieves the list of tools,
        converts each one to Ollama format, and returns the list.

        Returns:
            List of tool dicts with keys: type, function (name, description, parameters).

        Raises:
            ConnectionError: If the MCP server is unreachable.
        """
        # ******************************* START HERE *******************************
        #
        # This method is synchronous. Internally it calls an async method.
        # Use asyncio.run() to run the async implementation:
        #
        #   try:
        #       return asyncio.run(self._list_tools_async())
        #   except httpx.ConnectError as exc:
        #       raise ConnectionError(f"MCP server unreachable: {exc}") from exc
        #
        raise NotImplementedError("Implement list_tools()")
        # ******************************** END HERE ********************************

    def call_tool(self, name: str, arguments: dict) -> dict:
        """Call a named MCP tool and return the parsed result.

        Opens a connection to the MCP server, sends the tool call using
        MCP protocol semantics, and returns the parsed JSON result.

        Args:
            name: Tool name as returned by list_tools (e.g. "add_task").
            arguments: Dict of tool arguments validated by TaskParser.

        Returns:
            Parsed result dict from the MCP server, e.g.:
            {"success": True, "timestamp": "...", "csv_path": "..."}

        Raises:
            ConnectionError: If the MCP server is unreachable.
            RuntimeError: If the tool call fails.
        """
        logger.info("Calling MCP tool %r with: %s", name, arguments)
        # ******************************* START HERE *******************************
        #
        # Same synchronous wrapper pattern as list_tools().
        # Use asyncio.run() to call self._call_tool_async(name, arguments).
        # Catch httpx.ConnectError and re-raise as ConnectionError.
        #
        raise NotImplementedError("Implement call_tool()")
        # ******************************** END HERE ********************************

    async def _with_session(self, fn):
        """Open an MCP session, run fn(session), and return the result.

        This method handles the low-level MCP connection lifecycle:
          1. Opens an HTTP transport to the MCP server.
          2. Creates a ClientSession (the MCP protocol layer).
          3. Sends the MCP 'initialize' handshake.
          4. Runs your function with the live session.
          5. Cleans up automatically (async context managers).

        You do NOT need to modify this method — it is provided as scaffolding.
        Use it in _list_tools_async and _call_tool_async.

        Args:
            fn: Async callable that accepts a ClientSession and returns a result.

        Returns:
            Whatever fn(session) returns.
        """
        async with streamable_http_client(self._url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await fn(session)

    async def _list_tools_async(self) -> list[dict]:
        """Async implementation — fetches the tool list from the MCP server.

        Uses self._with_session() to open a session, then calls
        session.list_tools() to get the raw MCP tool list, and converts
        each tool to Ollama format.

        Returns:
            List of tool dicts in Ollama function-calling format.
        """
        # ******************************* START HERE *******************************
        #
        # Define an async inner function that receives a session, calls
        # session.list_tools(), and converts the results.
        #
        # Pattern:
        #   async def fn(session):
        #       result = await session.list_tools()
        #       # result.tools is a list of MCP Tool objects
        #       return [_mcp_tool_to_ollama(tool) for tool in result.tools]
        #   return await self._with_session(fn)
        #
        raise NotImplementedError("Implement _list_tools_async()")
        # ******************************** END HERE ********************************

    async def _call_tool_async(self, name: str, arguments: dict) -> dict:
        """Async implementation — calls the named tool and returns the result dict.

        Uses self._with_session() to open a session, then calls
        session.call_tool() with the tool name and arguments.
        The MCP server returns a result whose content[0].text is a JSON string.

        Args:
            name: Tool name (e.g. "add_task").
            arguments: Validated argument dict.

        Returns:
            Parsed dict from the server's JSON response.
        """
        # ******************************* START HERE *******************************
        #
        # Define an async inner function that receives a session, calls
        # session.call_tool(), extracts the text result, logs it, and parses it.
        #
        # Pattern:
        #   async def fn(session):
        #       result = await session.call_tool(name, arguments)
        #       text = result.content[0].text        # JSON string from server
        #       logger.info("MCP %r result: %s", name, text)
        #       return json.loads(text)
        #   return await self._with_session(fn)
        #
        raise NotImplementedError("Implement _call_tool_async()")
        # ******************************** END HERE ********************************
