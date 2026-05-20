"""Logging setup for the application."""

import logging
import sys
from pathlib import Path

from src.mcp_todo_host.config import Config


def setup_logging(config: Config) -> None:
    """Configure the root logger with a file handler and a console handler.

    Args:
        config: Loaded Config instance. Uses config.log_level and config.log_file.
    """
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, config.log_level.upper(), logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
