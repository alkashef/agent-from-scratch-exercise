"""Configuration module for csv_todo_mcp.

Loads runtime settings from a .env file and exposes them as a typed dataclass.
Owns no mutable state — callers create Config instances via load_config().
"""

from dataclasses import dataclass
from dotenv import dotenv_values


@dataclass
class Config:
    """Immutable runtime configuration for the MCP server.

    Attributes:
        csv_path: Filesystem path to the CSV to-do file.
        host: Host address the HTTP server binds to.
        port: TCP port the HTTP server listens on.
        log_level: Logging level string (e.g. 'INFO', 'DEBUG').
        log_file: Filesystem path for the log file output.
    """

    csv_path: str
    host: str
    port: int
    log_level: str
    log_file: str


def load_config(env_path: str) -> Config:
    """Load configuration from a .env file and return a Config instance.

    Args:
        env_path: Path to the .env file (e.g. 'config/.env').

    Returns:
        A Config populated with values from the .env file.

    Raises:
        KeyError: If a required variable is missing from the .env file.
        ValueError: If MCP_PORT cannot be parsed as an integer.
    """
    values = dotenv_values(env_path)
    return Config(
        csv_path=values["TODO_CSV_PATH"],
        host=values["MCP_HOST"],
        port=int(values["MCP_PORT"]),
        log_level=values.get("LOG_LEVEL", "INFO"),
        log_file=values.get("LOG_FILE", "./logs/server.log"),
    )
