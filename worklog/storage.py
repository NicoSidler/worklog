# worklog/storage.py
# SQLite storage layer with proper CRUD operations

from __future__ import annotations

from pathlib import Path
import sqlite3

from .models import WorkEntry


BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "work_log.db"


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_FILE)


def initialize_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                project TEXT NOT NULL,
                minutes INTEGER NOT NULL
            )
            """
        )


# ---------- CRUD ----------

def add_entry(entry: WorkEntry) -> None:
    initialize_database()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO entries (day, project, minutes) VALUES (?, ?, ?)",
            (entry.day.isoformat(), entry.project, entry.minutes),
        )


def load_entries() -> list[WorkEntry]:
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT day, project, minutes FROM entries"
        ).fetchall()

    entries: list[WorkEntry] = []

    for day, project, minutes in rows:
        entries.append(
            WorkEntry(
                day=WorkEntry.from_row(
                    {"date": day, "project": project, "minutes": str(minutes)}
                ).day,
                project=project,
                minutes=minutes,
            )
        )

    return entries


def delete_all_entries() -> None:
    initialize_database()

    with get_connection() as conn:
        conn.execute("DELETE FROM entries")
