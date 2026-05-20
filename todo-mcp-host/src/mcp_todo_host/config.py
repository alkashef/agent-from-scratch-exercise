"""Configuration loading from .env file."""

from dataclasses import dataclass
from dotenv import dotenv_values


_REQUIRED = ("MCP_SERVER_URL", "OLLAMA_BASE_URL", "OLLAMA_MODEL", "LLM_SYSTEM_PROMPT_PATH")
_DEFAULTS = {"LOG_LEVEL": "INFO", "LOG_FILE": "./logs/host.log"}


@dataclass
class Config:
    """Immutable runtime configuration loaded from a .env file.

    Owns: all runtime settings (URLs, model name, paths, log config).
    """

    mcp_server_url: str
    ollama_base_url: str
    ollama_model: str
    llm_system_prompt_path: str
    log_level: str
    log_file: str

    @classmethod
    def from_env(cls, dotenv_path: str = "config/.env") -> "Config":
        """Load configuration from a .env file.

        Args:
            dotenv_path: Path to the .env file.
        Returns:
            Populated Config instance.
        Raises:
            ValueError: If any required field is missing from the file.
        """
        values = {**_DEFAULTS, **dotenv_values(dotenv_path)}
        missing = [k for k in _REQUIRED if not values.get(k)]
        if missing:
            raise ValueError(f"Missing required config fields: {', '.join(missing)}")
        return cls(
            mcp_server_url=values["MCP_SERVER_URL"],
            ollama_base_url=values["OLLAMA_BASE_URL"],
            ollama_model=values["OLLAMA_MODEL"],
            llm_system_prompt_path=values["LLM_SYSTEM_PROMPT_PATH"],
            log_level=values["LOG_LEVEL"],
            log_file=values["LOG_FILE"],
        )
