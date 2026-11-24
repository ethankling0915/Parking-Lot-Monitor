"""Append-only event log in SQLite."""
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    ts REAL NOT NULL,
    kind TEXT NOT NULL,
    zone TEXT,
    detail TEXT
)
"""


class EventLog:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def log(self, kind, zone=None, detail=None, ts=None):
        self.conn.execute(
            "INSERT INTO events (ts, kind, zone, detail) VALUES (?, ?, ?, ?)",
            (ts if ts is not None else time.time(), kind, zone, detail),
        )
        self.conn.commit()
