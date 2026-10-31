"""Yagona Telegram bot moduliga (`backend/app/bot/bot.py`) yo'naltiruvchi qobiq.

Ishga tushirish:  python bot/bot.py  yoki  cd backend && python -m app.bot.bot
"""

import asyncio
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.bot.bot import (  # noqa: E402,F401
    API_URL,
    BOT_TOKEN,
    MENU,
    SITE_URL,
    api_get,
    article_buttons,
    article_text,
    dp,
    main,
    public_site_url,
    send_articles,
)

if __name__ == "__main__":
    asyncio.run(main())
