# bot/database.py - Per-user SQLite database for conversation history.

import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def get_user_db_path(user_id: int) -> Path:
    """Return path to user-specific database file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"{user_id}.db"


def get_db(user_id: int):
    """Return connection to user's database, creating tables if needed."""
    db_path = get_user_db_path(user_id)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,      -- 'user' or 'assistant'
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)")
    conn.commit()
    return conn


def save_message(user_id: int, role: str, content: str):
    """Save a message to user's database."""
    with get_db(user_id) as conn:
        conn.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)", (role, content)
        )
        conn.commit()


def get_history(user_id: int, limit: int = 10):
    """Retrieve last N messages for a user (oldest to newest)."""
    with get_db(user_id) as conn:
        rows = conn.execute(
            "SELECT role, content FROM conversations ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return list(reversed(rows))  # chronological order
