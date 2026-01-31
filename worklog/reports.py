# worklog/reports.py
# Topic: reporting and summaries
# Goal: compute totals without touching CSV read/write logic

from __future__ import annotations

from collections import defaultdict

from .models import WorkEntry


def minutes_to_hhmm(total_minutes: int) -> str:
    # Convert minutes into "H:MM"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{minutes:02d}"


def totals_by_project(entries: list[WorkEntry]) -> dict[str, int]:
    # Return a dict mapping project -> total minutes.
    totals = defaultdict(int)

    for e in entries:
        totals[e.project] += e.minutes

    return dict(totals)

from datetime import date


def summary(entries: list["WorkEntry"]) -> dict[str, int | float]:
    """
    Compute overall summary statistics.
    Returns a dict with numeric values only (easy to reuse).
    """
    if len(entries) == 0:
        return {
            "entries": 0,
            "total_minutes": 0,
            "days": 0,
            "avg_minutes_per_day": 0.0,
        }

    total_minutes = 0
    days_seen: set[date] = set()

    for e in entries:
        total_minutes += e.minutes
        days_seen.add(e.day)

    avg = total_minutes / len(days_seen)

    return {
        "entries": len(entries),
        "total_minutes": total_minutes,
        "days": len(days_seen),
        "avg_minutes_per_day": avg,
    }
