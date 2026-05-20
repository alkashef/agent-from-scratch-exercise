"""CSV repository for appending task records to a local file.

Owns the path to the CSV file and manages file creation and row appending.
All state is passed through the constructor — no global variables.
"""

import csv
from datetime import datetime, timezone
from pathlib import Path


_HEADER = ["timestamp", "description", "status", "category", "people", "deadline"]


class CsvRepository:
    """Appends task records to a CSV file on disk.

    Creates the file and parent directories on first write.
    Writes the CSV header exactly once (when the file is new or empty).

    Attributes:
        csv_path: Path to the managed CSV file.
    """

    def __init__(self, csv_path: str) -> None:
        """Set the target CSV file path.

        Args:
            csv_path: Filesystem path to the CSV file.
                      Created on first call to append_task if absent.
        """
        self.csv_path = csv_path

    def append_task(
        self,
        description: str,
        status: str = "todo",
        category: str = "",
        people: str = "",
        deadline: str = "",
    ) -> dict:
        """Append one task record to the CSV file and return the written row.

        Creates the file and any missing parent directories on first call.
        Writes the header row exactly once (skipped when file already has content).

        Args:
            description: Human-readable task description.
            status: Task status string (default "todo").
            category: Optional category label.
            people: Optional comma-separated people names.
            deadline: Optional deadline string.

        Returns:
            Dict with keys: timestamp, description, status, category, people,
            deadline, csv_path.
        """
        path = Path(self.csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        is_new = not path.exists() or path.stat().st_size == 0
        timestamp = datetime.now(timezone.utc).isoformat()

        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(_HEADER)
            writer.writerow([timestamp, description, status, category, people, deadline])

        return {
            "timestamp": timestamp,
            "description": description,
            "status": status,
            "category": category,
            "people": people,
            "deadline": deadline,
            "csv_path": str(path),
        }
