"""SQLite initialization and schema migration for memory DB."""
import logging
import sqlite3
from pathlib import Path

from common.config import DATA_DIR, MEMORY_DB_PATH

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
"""


def ensure_data_dir() -> None:
    """Create data/ directory if it does not exist."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error("Ошибка при создании каталога data: %s", e)
        raise


def get_connection() -> sqlite3.Connection:
    """Return a connection to the memory DB. Ensures data dir and schema exist."""
    ensure_data_dir()
    try:
        conn = sqlite3.connect(str(MEMORY_DB_PATH))
        conn.executescript(_SCHEMA)
        conn.commit()
        return conn
    except sqlite3.Error as e:
        logger.error("Ошибка при инициализации БД: %s", e)
        raise


def init_db() -> None:
    """Ensure DB file and table exist. Call at bot startup."""
    conn = get_connection()
    try:
        conn.close()
    except Exception:
        pass
