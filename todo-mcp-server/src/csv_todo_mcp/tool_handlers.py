"""MCP tool handler for the add_task tool.

Validates tool input, delegates to CsvRepository, and returns the MCP result dict.
No state is owned here — the repository is passed in.
"""

import logging

from csv_todo_mcp.csv_repository import CsvRepository

logger = logging.getLogger(__name__)


def add_task_handler(args: dict, repo: CsvRepository) -> dict:
    """Validate args and append one task to the CSV via repo.

    Args:
        args: Dict of tool input fields (description, status, category, people, deadline).
        repo: CsvRepository instance to delegate the write to.

    Returns:
        On success: {"success": True, "timestamp": str, "csv_path": str}
        On validation error: {"success": False, "error": str}
    """
    description = args.get("description", "")
    if not isinstance(description, str) or not description.strip():
        error_msg = "description is required and must be a non-empty string"
        logger.error("add_task validation error: %s", error_msg)
        raise ValueError(error_msg)

    status = args.get("status", "todo")
    category = args.get("category", "")
    people = args.get("people", "")
    deadline = args.get("deadline", "")

    logger.info("add_task called: description=%r status=%r", description, status)

    result = repo.append_task(
        description=description,
        status=status,
        category=category,
        people=people,
        deadline=deadline,
    )

    logger.info("Task appended → %s (at %s)", result["csv_path"], result["timestamp"])

    return {
        "success": True,
        "timestamp": result["timestamp"],
        "csv_path": result["csv_path"],
    }
