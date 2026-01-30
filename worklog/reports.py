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
