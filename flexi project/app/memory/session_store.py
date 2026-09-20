"""
app/memory/session_store.py
Unit 1 — SQLite-based persistent session memory for AI agents.

Stores multi-turn conversation history keyed by session_id.
Agents can retrieve full history to maintain context across interactions.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("SQLITE_DB_PATH", "./defect_memory.db")


def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection, creating the DB and tables if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL,          -- 'user' | 'assistant' | 'system'
            content     TEXT NOT NULL,
            timestamp   TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS defect_reports (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            title           TEXT,
            description     TEXT,
            component       TEXT,
            severity        TEXT,
            report_json     TEXT,
            created_at      TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_message(session_id: str, role: str, content: str) -> None:
    """Persist a single message to the session history."""
    conn = _get_connection()
    conn.execute(
        "INSERT INTO sessions (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 20) -> list[dict]:
    """Retrieve recent conversation history for a session."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT role, content, timestamp FROM sessions "
        "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    ).fetchall()
    conn.close()
    # Return in chronological order
    return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in reversed(rows)]


def save_defect_report(session_id: str, report: dict) -> None:
    """Save a finalised defect report to the database."""
    conn = _get_connection()
    conn.execute(
        """INSERT INTO defect_reports
           (session_id, title, description, component, severity, report_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            session_id,
            report.get("title", ""),
            report.get("description", ""),
            report.get("component", ""),
            report.get("severity", ""),
            json.dumps(report),
            datetime.utcnow().isoformat(),
        )
    )
    conn.commit()
    conn.close()


def get_all_defect_reports() -> list[dict]:
    """Retrieve all defect reports from the database."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT session_id, title, component, severity, report_json, created_at "
        "FROM defect_reports ORDER BY id DESC"
    ).fetchall()
    conn.close()
    results = []
    for row in rows:
        try:
            report = json.loads(row[3] if row[3] else "{}")
        except Exception:
            report = {}
        report.update({
            "session_id": row[0],
            "title": row[1],
            "component": row[2],
            "severity": row[3],
            "created_at": row[5],
        })
        results.append(report)
    return results


def clear_session(session_id: str) -> None:
    """Remove all messages for a given session (start fresh)."""
    conn = _get_connection()
    conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Quick smoke test
    sid = "test-session-001"
    save_message(sid, "user", "Login page crashes on submit")
    save_message(sid, "assistant", "I'll analyze this defect for you.")
    history = get_history(sid)
    print("Session history:", json.dumps(history, indent=2))
    clear_session(sid)
    print("Session cleared.")
