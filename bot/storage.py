"""Yagona bot saqlash moduliga (`backend/app/bot/storage.py`) yo'naltiruvchi qobiq."""

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.bot.storage import (  # noqa: E402,F401
    DB_PATH,
    disable_notifications,
    ensure_user,
    get_saved,
    notification_subscribers,
    save_article,
    toggle_notifications,
)
