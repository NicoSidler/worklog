# worklog/storage.py
# Topic: CSV storage for the work log
# Goal: load WorkEntry objects from CSV, and save them back to CSV

from __future__ import annotations

from pathlib import Path
import csv

from .models import WorkEntry


# BASE_DIR is the folder where this module file lives (worklog/).
BASE_DIR = Path(__file__).resolve().parent

# Store the CSV next to this package (worklog/work_log.csv).
DATA_FILE = BASE_DIR / "work_log.csv"

# CSV columns (header row)
FIELDNAMES = ["date", "project", "minutes"]


def load_entries() -> list[WorkEntry]:
    # Load work entries from CSV into WorkEntry objects.
    if not DATA_FILE.exists():
        return []

    entries: list[WorkEntry] = []

    with DATA_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = WorkEntry.from_row(row)
            if entry is not None:
                entries.append(entry)

    return entries


def save_entries(entries: list[WorkEntry]) -> None:
    # Save WorkEntry objects to CSV.
    with DATA_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_row())
