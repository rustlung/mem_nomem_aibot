"""CRUD for user message history: add_message, get_context, clear_user, trim_user."""
import logging
from datetime import datetime, timezone
from typing import Any

from common.config import HISTORY_PAIRS_LIMIT
from common.db import ensure_data_dir, get_connection

logger = logging.getLogger(__name__)

LIMIT_ROWS = HISTORY_PAIRS_LIMIT * 2  # N pairs = 2*N rows


def add_message(user_id: int, role: str, content: str) -> None:
    """Append one message and trim user history to last N pairs."""
    ensure_data_dir()
    try:
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (user_id, role, content, datetime.now(tz=timezone.utc).isoformat()),
            )
            conn.commit()
        finally:
            conn.close()
        trim_user(user_id)
    except Exception as e:
        logger.error("Ошибка при записи в БД: %s", e)
        raise


def get_context(user_id: int) -> list[dict[str, Any]]:
    """
    Return last 2*N messages for user in chronological order.
    Each dict: {"role": "user"|"assistant", "content": "..."}.
    """
    ensure_data_dir()
    try:
        conn = get_connection()
        try:
            cur = conn.execute(
                """
                SELECT role, content FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, LIMIT_ROWS),
            )
            rows = cur.fetchall()
        finally:
            conn.close()
        # Reverse to chronological order
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
    except Exception as e:
        logger.error("Ошибка при чтении БД: %s", e)
        raise


def clear_user(user_id: int) -> None:
    """Delete all messages for the given user."""
    ensure_data_dir()
    try:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        logger.error("Ошибка при очистке контекста пользователя: %s", e)
        raise


def trim_user(user_id: int) -> None:
    """Keep only the last N pairs (2*N rows) for this user. Delete older rows."""
    ensure_data_dir()
    try:
        conn = get_connection()
        try:
            conn.execute(
                """
                DELETE FROM messages WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM messages WHERE user_id = ?
                    ORDER BY id DESC LIMIT ?
                )
                """,
                (user_id, user_id, LIMIT_ROWS),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        logger.error("Ошибка при обрезке контекста пользователя: %s", e)
        raise
