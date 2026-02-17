# worklog/models.py
# Topic: dataclass model for one work entry
# Goal: represent data cleanly, and convert to/from CSV rows

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class WorkEntry:
    id: Optional[int]  # None before insert
    day: date
    project: str
    minutes: int


    @staticmethod
    def from_row(row: dict[str, str]) -> "WorkEntry | None":
        # Convert CSV row text into a WorkEntry object.
        day_text = row.get("date", "").strip()
        project = row.get("project", "").strip()
        minutes_text = row.get("minutes", "").strip()

        # Parse date (YYYY-MM-DD)
        try:
            day_value = date.fromisoformat(day_text)
        except ValueError:
            return None

        # Parse minutes (must be whole number)
        try:
            minutes_value = int(minutes_text)
        except ValueError:
            return None

        # Reject negative minutes
        if minutes_value < 0:
            return None

        # Normalize empty project label
        if project == "":
            project = "(no project)"

        return WorkEntry(day=day_value, project=project, minutes=minutes_value)

    def to_row(self) -> dict[str, str]:
        # Convert WorkEntry back to a CSV row (strings).
        return {
            "date": self.day.isoformat(),
            "project": self.project,
            "minutes": str(self.minutes),
        }
