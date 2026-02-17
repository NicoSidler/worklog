# worklog/storage.py
# SQLite storage layer with proper CRUD operations

from __future__ import annotations

from pathlib import Path
import sqlite3

from .models import WorkEntry
from datetime import date



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
        cursor = conn.execute(
            "INSERT INTO entries (day, project, minutes) VALUES (?, ?, ?)",
            (entry.day.isoformat(), entry.project, entry.minutes),
        )
        entry.id = cursor.lastrowid


def load_entries() -> list[WorkEntry]:
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, day, project, minutes FROM entries"
        ).fetchall()

    entries: list[WorkEntry] = []

    for row_id, day, project, minutes in rows:
        entries.append(
            WorkEntry(
                id=row_id,
                day=date.fromisoformat(day),
                project=project,
                minutes=minutes,
            )
        )

    return entries



def delete_all_entries() -> None:
    initialize_database()

    with get_connection() as conn:
        conn.execute("DELETE FROM entries")

def delete_entry(entry_id: int) -> None:
    initialize_database()

    with get_connection() as conn:
        conn.execute(
            "DELETE FROM entries WHERE id = ?",
            (entry_id,),
        )
