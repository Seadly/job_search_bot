import sqlite3
import json
from datetime import datetime
from typing import Optional


DB_PATH = "job_bot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Создаёт таблицы если их нет."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS keywords (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                keyword     TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now')),
                UNIQUE(user_id, keyword),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS channels (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                channel     TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now')),
                UNIQUE(user_id, channel),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                enabled     INTEGER DEFAULT 1,
                UNIQUE(user_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)


# ── Users ──────────────────────────────────────────────────────────────────────

def upsert_user(user_id: int, username: Optional[str], full_name: str):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO users (user_id, username, full_name)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name""",
            (user_id, username, full_name),
        )


# ── Keywords ───────────────────────────────────────────────────────────────────

def get_keywords(user_id: int) -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT keyword FROM keywords WHERE user_id=? ORDER BY created_at",
            (user_id,),
        ).fetchall()
    return [r["keyword"] for r in rows]


def add_keyword(user_id: int, keyword: str) -> bool:
    """Возвращает True если добавлено, False если уже существует."""
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO keywords (user_id, keyword) VALUES (?, ?)",
                (user_id, keyword.lower().strip()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def remove_keyword(user_id: int, keyword: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM keywords WHERE user_id=? AND keyword=?",
            (user_id, keyword.lower().strip()),
        )
    return cur.rowcount > 0


def clear_keywords(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM keywords WHERE user_id=?", (user_id,))


# ── Channels ───────────────────────────────────────────────────────────────────

def get_channels(user_id: int) -> list[str]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT channel FROM channels WHERE user_id=? ORDER BY created_at",
            (user_id,),
        ).fetchall()
    return [r["channel"] for r in rows]


def add_channel(user_id: int, channel: str) -> bool:
    channel = channel.lstrip("@").strip()
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO channels (user_id, channel) VALUES (?, ?)",
                (user_id, channel),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def remove_channel(user_id: int, channel: str) -> bool:
    channel = channel.lstrip("@").strip()
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM channels WHERE user_id=? AND channel=?",
            (user_id, channel),
        )
    return cur.rowcount > 0


# ── Alerts ─────────────────────────────────────────────────────────────────────

def get_alerts_enabled(user_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT enabled FROM alerts WHERE user_id=?", (user_id,)
        ).fetchone()
    return bool(row["enabled"]) if row else False


def set_alerts(user_id: int, enabled: bool):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO alerts (user_id, enabled) VALUES (?, ?)
               ON CONFLICT(user_id) DO UPDATE SET enabled=excluded.enabled""",
            (user_id, int(enabled)),
        )


def get_all_alert_users() -> list[int]:
    """Возвращает всех пользователей с включёнными уведомлениями."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT user_id FROM alerts WHERE enabled=1"
        ).fetchall()
    return [r["user_id"] for r in rows]
