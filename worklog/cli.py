# worklog/cli.py
# Topic: argparse (command-line interface)
# Goal: run your worklog package using commands instead of a menu

from __future__ import annotations
from . import __version__
import argparse
from datetime import date

from .storage import load_entries, add_entry, DB_FILE
from .models import WorkEntry
from .reports import totals_by_project, minutes_to_hhmm

import argparse
from datetime import date, timedelta
from pathlib import Path
import json
from .reports import totals_by_project, minutes_to_hhmm, summary

from .storage import load_entries, add_entry, delete_entry, DB_FILE



def parse_date_iso(text: str) -> date:
    # Convert "YYYY-MM-DD" into a date object, or raise an argparse error.
    try:
        return date.fromisoformat(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD, for example 2026-01-26.") from e


def parse_minutes(text: str) -> int:
    # Convert text to int minutes, also validate it.
    try:
        minutes = int(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError("Minutes must be a whole number, for example 45.") from e

    if minutes < 0:
        raise argparse.ArgumentTypeError("Minutes cannot be negative.")

    return minutes

def filter_by_date_range(entries: list[WorkEntry], start: date, end: date) -> list[WorkEntry]:
    # Return only entries where start <= entry.day <= end
    if end < start:
        start, end = end, start  # swap if user gave them backwards

    return [e for e in entries if start <= e.day <= end]


def cmd_list(args: argparse.Namespace) -> None:
    # List entries, optionally filter by project.
    entries = load_entries()

    if args.project is not None:
        entries = [e for e in entries if e.project == args.project]

    if len(entries) == 0:
        print("No entries.")
        return

    entries_sorted = sorted(entries, key=lambda e: e.day, reverse=True)

    for i, e in enumerate(entries_sorted, start=1):
        print(f"{e.id}) {e.day.isoformat()} | {e.project} | {e.minutes} min")



def cmd_totals(args: argparse.Namespace) -> None:
    # Show total minutes per project, optionally filtered by a single project.
    entries = load_entries()

    if args.project is not None:
        entries = [e for e in entries if e.project == args.project]

    if len(entries) == 0:
        print("No entries.")
        return

    totals = totals_by_project(entries)
    items_sorted = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    grand_total = 0
    for project, mins in items_sorted:
        grand_total += mins
        print(f"- {project}: {mins} min ({minutes_to_hhmm(mins)})")

    print(f"Total: {grand_total} min ({minutes_to_hhmm(grand_total)})")


def cmd_add(args: argparse.Namespace) -> None:
    entry = WorkEntry(id=None, day=args.date, project=args.project, minutes=args.minutes)
    add_entry(entry)
    print(f"Added entry with id={entry.id}")


def cmd_report(args: argparse.Namespace) -> None:
    # Report totals by project in a date range.
    entries = load_entries()

    # Default behavior: if user did not provide dates, use last 7 days.
    # (We still allow explicit --start/--end.)
    if args.start is None or args.end is None:
        today = date.today()
        start = today - timedelta(days=6)  # last 7 days including today
        end = today
    else:
        start = args.start
        end = args.end

    entries = filter_by_date_range(entries, start, end)

    report = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "count": len(entries),
        "totals_by_project": {},
        "grand_total_minutes": 0,
        # Optional: you can include these even when empty if you prefer
        # "totals_by_project_hhmm": {},
        # "grand_total_hhmm": "0:00",
    }

    if len(entries) == 0:
        print(f"No entries in range {start.isoformat()} to {end.isoformat()}.")
    else:
        totals = totals_by_project(entries)
        items_sorted = sorted(totals.items(), key=lambda x: x[1], reverse=True)

        grand_total = 0
        print(f"Report {start.isoformat()} to {end.isoformat()} ({len(entries)} entries)")
        for project, mins in items_sorted:
            grand_total += mins
            print(f"- {project}: {mins} min ({minutes_to_hhmm(mins)})")
            report["totals_by_project"][project] = mins

        report["grand_total_minutes"] = grand_total

        # ✅ ADD THESE LINES
        report["grand_total_hhmm"] = minutes_to_hhmm(grand_total)
        report["totals_by_project_hhmm"] = {
            project: minutes_to_hhmm(mins) for project, mins in report["totals_by_project"].items()
        }

        print(f"Total: {grand_total} min ({minutes_to_hhmm(grand_total)})")

    # Optional JSON export
    if args.json is not None:
        out_path = Path(args.json)
        out_text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
        out_path.write_text(out_text, encoding="utf-8")
        print(f"Wrote JSON report to {out_path.resolve()}")

def cmd_summary(args: argparse.Namespace) -> None:
    entries = load_entries()

    data = summary(entries)

    print("Summary")
    print(f"- Entries: {data['entries']}")
    print(f"- Total minutes: {data['total_minutes']} min ({minutes_to_hhmm(data['total_minutes'])})")
    print(f"- Days with entries: {data['days']}")

    if data["days"] > 0:
        print(f"- Average per day: {data['avg_minutes_per_day']:.1f} min")


def build_parser() -> argparse.ArgumentParser:
    # Create the main parser and subcommands.
    parser = argparse.ArgumentParser(
        prog="worklog",
        description="Track work time and generate summaries.",
        epilog=(
            "Examples:\n"
            "  py -m worklog add --date 2026-01-26 --project Thesis --minutes 45\n"
            "  py -m worklog list\n"
            "  py -m worklog totals\n"
            "  py -m worklog report --start 2026-01-01 --end 2026-01-31 --json january.json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global option (works with any command)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit.",
    )

    # Subcommands (list, totals, add, report, ...)
    subparsers = parser.add_subparsers(dest="command", required=True)



    
    # Command: list
    p_list = subparsers.add_parser("list", help="List entries (newest first).")
    p_list.add_argument("--project", help="Only show entries for this project.")
    p_list.set_defaults(func=cmd_list)

    # Command: totals
    p_totals = subparsers.add_parser("totals", help="Show totals by project.")
    p_totals.add_argument("--project", help="Only total one project.")
    p_totals.set_defaults(func=cmd_totals)

    # Command: add
    p_add = subparsers.add_parser("add", help="Add one entry.")
    p_add.add_argument("--date", required=True, type=parse_date_iso, help="Date as YYYY-MM-DD.")
    p_add.add_argument("--project", required=True, help="Project name, for example Thesis.")
    p_add.add_argument("--minutes", required=True, type=parse_minutes, help="Minutes as a whole number.")
    p_add.set_defaults(func=cmd_add)

    # Command: report
    p_report = subparsers.add_parser("report", help="Totals by project for a date range (default last 7 days).")
    p_report.add_argument("--start", type=parse_date_iso, help="Start date YYYY-MM-DD (optional).")
    p_report.add_argument("--end", type=parse_date_iso, help="End date YYYY-MM-DD (optional).")
    p_report.add_argument("--json", help="Write the report to a JSON file (optional).")
    p_report.set_defaults(func=cmd_report)

    # Command: summary
    p_summary = subparsers.add_parser(
        "summary",
        help="Show overall summary statistics."
    )
    p_summary.set_defaults(func=cmd_summary)

    p_delete = subparsers.add_parser("delete", help="Delete entry by id.")
    p_delete.add_argument("--id", required=True, type=int, help="ID of entry to delete.")
    p_delete.set_defaults(func=cmd_delete)

  
    return parser


def main(argv: list[str] | None = None) -> None:
    # Parse command-line arguments and run the correct command function.
    parser = build_parser()
    args = parser.parse_args(argv)

    # Each subcommand set args.func to the right function.
    args.func(args)

def cmd_delete(args: argparse.Namespace) -> None:
    delete_entry(args.id)
    print(f"Deleted entry with id={args.id}")

