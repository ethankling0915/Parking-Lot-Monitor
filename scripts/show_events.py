"""Print events from a database with their video timestamps.
Usage: python scripts/show_events.py <db_path> [kind_prefix]
Example: python scripts/show_events.py data/test_day2.db my_car
"""
import sqlite3
import sys

db_path = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else ""

rows = sqlite3.connect(db_path).execute(
    "SELECT ts, kind, zone FROM events WHERE kind LIKE ? ORDER BY ts",
    (prefix + "%",),
)
for ts, kind, zone in rows:
    print(f"{ts:10.1f}s  {kind:<16} {zone or ''}")