"""
RuleLock AI — Component 4: append-only audit log
Owner: Mishen

Every automated action gets written here BEFORE the response returns —
a record of what the system already did, not a queue waiting on a
human decision. Uses SQLite for local dev/CI; point AUDIT_LOG at the
shared Postgres `audit_log` table (see data-collection/schema.sql) for
the integrated demo.
"""
import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.environ.get("AUDIT_LOG_PATH", "audit_log.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            action TEXT NOT NULL,
            reason TEXT,
            "timestamp" TEXT NOT NULL
        )
    """)
    return conn


def record(order_id: str, action: str, reason: str) -> None:
    conn = _get_conn()
    conn.execute(
        'INSERT INTO audit_log (order_id, action, reason, "timestamp") VALUES (?, ?, ?, ?)',
        (order_id, action, reason, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def all_entries() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute('SELECT order_id, action, reason, "timestamp" FROM audit_log').fetchall()
    conn.close()
    return [{"order_id": r[0], "action": r[1], "reason": r[2], "timestamp": r[3]} for r in rows]
