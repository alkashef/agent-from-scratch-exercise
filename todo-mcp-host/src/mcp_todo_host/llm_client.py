"""Ollama LLM client wrapper."""

import logging
from datetime import date
from pathlib import Path

import httpx
import ollama

from src.mcp_todo_host.config import Config

logger = logging.getLogger(__name__)


class LlmClient:
    """Sends user text and tool definitions to a local Ollama model and returns the tool call.

    Owns the ollama.Client instance and the loaded system prompt text.
    """

    def __init__(self, config: Config) -> None:
        """Initialise the LLM client.

        Args:
            config: Application configuration.
        """
        self._model = config.ollama_model
        self._system_prompt = Path(config.llm_system_prompt_path).read_text(encoding="utf-8")
        self._client = ollama.Client(host=config.ollama_base_url)

    def generate(self, user_message: str, tools: list[dict]) -> dict:
        """Send user_message and available tools to the LLM and return the selected tool call.

        The LLM receives:
          - a system prompt (your instructions for how to behave)
          - the user's message
          - the list of available tools (name, description, input schema)

        When the LLM decides to use a tool it responds with a tool_call object
        instead of plain text. This method extracts that tool call and returns it.

        Args:
            user_message: The user's task description.
            tools: List of tool dicts in Ollama function format
                   (produced by McpClient.list_tools).

        Returns:
            Dict with keys:
              "name"      → the tool the LLM chose to call (e.g. "add_task")
              "arguments" → dict of arguments the LLM wants to pass (e.g. {"description": ...})

        Raises:
            ValueError: If the LLM does not invoke a tool.
            ConnectionError: If the Ollama server is unreachable.
        """
        # ******************************* START HERE *******************************
        #
        # 1. Inject today's date into the system prompt.
        #    The prompt contains the placeholder {TODAY}.
        #    Replace it with the current date formatted as DD/MM/YYYY.
        #
        #    today = date.today().strftime("%d/%m/%Y")
        #    system_content = self._system_prompt.replace("{TODAY}", today)
        #
        # 2. Build the messages list.
        #    An LLM conversation is a list of role/content dicts in order:
        #
        #    messages = [
        #        {"role": "system", "content": system_content},  # instructions
        #        {"role": "user",   "content": user_message},    # the user's input
        #    ]
        #
        # 3. Log the outgoing message at DEBUG level:
        #    logger.debug("Sending message to LLM: %s", user_message)
        #
        # 4. Call the Ollama chat API.
        #    Passing `tools` here is what enables function-calling:
        #    the model can now respond with a tool_call instead of text.
        #
        #    try:
        #        response = self._client.chat(model=self._model, messages=messages, tools=tools)
        #    except httpx.ConnectError as exc:
        #        raise ConnectionError(f"Ollama server unreachable: {exc}") from exc
        #
        # 5. Check whether the LLM actually called a tool.
        #    tool_calls = response.message.tool_calls
        #    If tool_calls is falsy (None or empty list), the model replied with
        #    text instead of a tool call — raise a ValueError so the caller knows.
        #
        # 6. Extract the first tool call and return it as a plain dict.
        #    tc = tool_calls[0]
        #    logger.debug("LLM tool call: %s %s", tc.function.name, tc.function.arguments)
        #    return {"name": tc.function.name, "arguments": tc.function.arguments}
        #
        raise NotImplementedError("Implement the LLM interaction here")
        # ******************************** END HERE ********************************
