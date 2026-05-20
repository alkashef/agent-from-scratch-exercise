"""Streamlit I/O adapter — read_msg / write_msg interface for the App."""

import streamlit as st

from src.mcp_todo_host.config import Config

_MESSAGES_KEY = "messages"


class ChatUI:
    """Streamlit chat interface that exposes read_msg() and write_msg() to the App.

    Conversation history lives in st.session_state across Streamlit re-runs.
    This class owns no mutable state itself.
    """

    def __init__(self, config: Config) -> None:
        """Render the page title and existing conversation history.

        Args:
            config: Application configuration (reserved for future use).
        """
        if _MESSAGES_KEY not in st.session_state:
            st.session_state[_MESSAGES_KEY] = []
        st.header("todo Agent")
        st.subheader("A minimal MCP Host that connects the todo MCP server to classify and write a task in a CSV file.")
        for message in st.session_state[_MESSAGES_KEY]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    def read_msg(self) -> str | None:
        """Return the current user input if submitted this run, else None.

        If input is present, adds the user bubble to history and renders it.

        Returns:
            User message string, or None if no input this run.
        """
        user_input = st.chat_input("Describe a task to add...")
        if user_input:
            st.session_state[_MESSAGES_KEY].append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
        return user_input or None

    def write_msg(self, msg: str) -> None:
        """Add an assistant message to history and render it.

        Args:
            msg: The message to display (success result or error string).
        """
        st.session_state[_MESSAGES_KEY].append({"role": "assistant", "content": msg})
        with st.chat_message("assistant"):
            st.write(msg)
