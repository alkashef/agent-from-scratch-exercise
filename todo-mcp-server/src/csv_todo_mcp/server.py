"""MCP server entry point for csv_todo_mcp.

Registers the add_task MCP tool and starts the Streamable HTTP server.
All state is passed through run_server — no global variables.
"""

import argparse
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from csv_todo_mcp.config import Config, load_config
from csv_todo_mcp.csv_repository import CsvRepository
from csv_todo_mcp.tool_handlers import add_task_handler

_LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s — %(message)s"


def _configure_logging(config: Config) -> logging.Logger:
    """Configure console and file handlers on the csv_todo_mcp logger.

    Args:
        config: Runtime configuration supplying log_level and log_file.

    Returns:
        The configured logger for the csv_todo_mcp package.
    """
    logger = logging.getLogger("csv_todo_mcp")
    logger.setLevel(config.log_level.upper())

    formatter = logging.Formatter(_LOG_FORMAT)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


def run_server(config: Config) -> None:
    """Start the MCP HTTP server with the add_task tool registered.

    Args:
        config: Runtime configuration (csv_path, host, port, log_level, log_file).
    """
    logger = _configure_logging(config)
    logger.info(
        "Server starting on %s:%d | csv=%s | log=%s",
        config.host, config.port, config.csv_path, config.log_file,
    )

    repo = CsvRepository(config.csv_path)
    mcp = FastMCP("csv-todo", host=config.host, port=config.port, json_response=True, stateless_http=True)

    @mcp.tool()
    def add_task(
        description: str,
        status: str = "todo",
        category: str = "",
        people: str = "",
        deadline: str = "",
    ) -> dict:
        """Append one task to the CSV to-do file.

        Args:
            description: Human-readable task description (required).
            status: Task status (default 'todo').
            category: Optional category label.
            people: Optional comma-separated people names.
            deadline: Optional deadline string.

        Returns:
            Dict with success, timestamp, and csv_path.
        """
        return add_task_handler(
            {
                "description": description,
                "status": status,
                "category": category,
                "people": people,
                "deadline": deadline,
            },
            repo,
        )

    try:
        mcp.run(transport="streamable-http")
    finally:
        logger.info("Server stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSV Todo MCP Server")
    parser.add_argument("--env-file", default="config/.env", help="Path to .env config file")
    args = parser.parse_args()
    run_server(load_config(args.env_file))
