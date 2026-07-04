import os
from dotenv import load_dotenv

load_dotenv()

# Ma'lumotlar bazasi: prod'da PostgreSQL, lokal ishlab chiqishda SQLite yetarli.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ainews.db")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-8")

# Admin panelga kirish uchun maxfiy token (X-Admin-Token sarlavhasi orqali).
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-token-o'zgartiring")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")  # masalan: @ai_news_uz

# Frontend manzili (CORS uchun)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
