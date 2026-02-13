"""Configuration loaded from environment with validation."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of common/)
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")


def get_env(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None or value.strip() == "":
        return default or ""
    return value.strip()


# Required keys for validation
REQUIRED_KEYS = ("BOT_NOMEM_TOKEN", "BOT_MEM_TOKEN", "OPENAI_API_KEY")


def validate_config(required: tuple[str, ...] = REQUIRED_KEYS) -> None:
    """Check that required env vars are set. On failure log and sys.exit(1)."""
    missing = [k for k in required if not get_env(k)]
    if missing:
        print(f"[ERROR] Не заданы переменные окружения: {', '.join(missing)}. Скопируйте .env.example в .env и заполните.", file=sys.stderr)
        sys.exit(1)


def validate_bot_nomem_config() -> None:
    """Validate env for bot_nomem: BOT_NOMEM_TOKEN, OPENAI_API_KEY."""
    validate_config(("BOT_NOMEM_TOKEN", "OPENAI_API_KEY"))


def validate_bot_mem_config() -> None:
    """Validate env for bot_mem: BOT_MEM_TOKEN, OPENAI_API_KEY."""
    validate_config(("BOT_MEM_TOKEN", "OPENAI_API_KEY"))


# OpenAI
OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_MODEL = get_env("OPENAI_MODEL", "gpt-4")

# Bot tokens (new names)
BOT_NOMEM_TOKEN = get_env("BOT_NOMEM_TOKEN")
BOT_MEM_TOKEN = get_env("BOT_MEM_TOKEN")

# Memory bot: max pairs (user+assistant) per user
def _parse_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default


HISTORY_PAIRS_LIMIT = max(1, _parse_int("HISTORY_PAIRS_LIMIT", 5))

# Path to SQLite DB (data/ created automatically)
DATA_DIR = _root / "data"
MEMORY_DB_PATH = DATA_DIR / "memory.db"
