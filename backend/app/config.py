import os
from dotenv import load_dotenv

load_dotenv()

# Ma'lumotlar bazasi: prod'da PostgreSQL, lokal ishlab chiqishda SQLite yetarli.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ainews.db")

# AI provayder: "gemini" (standart) yoki "claude"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Render kabi Google Cloud'dan tashqaridagi serverlar uchun Vertex AI + ADC.
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
VERTEX_GEMINI_MODEL = os.getenv("VERTEX_GEMINI_MODEL", "gemini-3.7-flash")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-8")

# Admin panelga kirish uchun maxfiy token (X-Admin-Token sarlavhasi orqali).
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
UNSAFE_ADMIN_TOKENS = {
    "admin-token-o'zgartiring",
    "maxfiy-admin-token",
    "bu-yerga-kuchli-tasodifiy-token-kiriting",
}


def admin_is_configured() -> bool:
    return len(ADMIN_TOKEN) >= 32 and ADMIN_TOKEN not in UNSAFE_ADMIN_TOKENS


def validate_production_settings() -> None:
    """Xavfli admin token haqida ogohlantiradi; public API'ni yiqitmaydi."""
    if not admin_is_configured():
        print(
            "OGOHLANTIRISH: ADMIN_TOKEN xavfsiz sozlanmagan. "
            "Admin endpointlari yangi kuchli token berilguncha bloklandi."
        )

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")  # masalan: @ai_news_uz


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "ha")


# Render kabi yagona web-service deploymentida pipeline va bot API jarayoni
# ichida ishlaydi. Docker Compose backend servisida bu qiymat false qilinadi.
RUN_BACKGROUND_SERVICES = _bool("RUN_BACKGROUND_SERVICES", "true")

# Sikllar orasidagi tanaffus. Qisqaroq oraliq = yangilik tezroq chiqadi.
PIPELINE_INTERVAL = int(os.getenv("PIPELINE_INTERVAL", "3600"))
# Har manbadan o'qiladigan eng yangi yozuvlar soni. Manba bir siklda shundan
# ko'p maqola chiqarsa, ortiqchasi butunlay yo'qoladi — keyingi sikl ham
# faqat eng yangilariga qaraydi.
PIPELINE_PER_FEED = int(os.getenv("PIPELINE_PER_FEED", "12"))

# Bir voqea turli manbalarda sal boshqacha sarlavha bilan chiqishi mumkin.
DUPLICATE_LOOKBACK_DAYS = int(os.getenv("DUPLICATE_LOOKBACK_DAYS", "30"))

# RSS faqat qisqa xulosa bersa, o'sha saytning maqola sahifasidan asosiy
# paragraflarni olish. So'rovlar parallel, lekin cheklangan holda bajariladi.
FETCH_FULL_ARTICLE = _bool("FETCH_FULL_ARTICLE", "true")
FULL_ARTICLE_MIN_SOURCE_CHARS = int(os.getenv("FULL_ARTICLE_MIN_SOURCE_CHARS", "1800"))
FULL_ARTICLE_MAX_CHARS = int(os.getenv("FULL_ARTICLE_MAX_CHARS", "12000"))
ARTICLE_FETCH_WORKERS = int(os.getenv("ARTICLE_FETCH_WORKERS", "4"))


# Avto-chop etish ixtiyoriy. Xavfsiz standartda maqolalar admin tasdig'ini kutadi.
# Faqat editorial jarayon tayyor bo'lsa AUTO_PUBLISH=true qiling.
AUTO_PUBLISH = _bool("AUTO_PUBLISH", "false")
# Shu bahodan pastlari pending'da qoladi va admin tasdig'ini kutadi.
# Kalibrlangan shkalada (ai_agent.SYSTEM_PROMPT) 1 — qo'llanma, marketing va
# fikr-mulohaza materiallari; 2 dan boshlab haqiqiy yangilik. Shkala
# o'zgartirilsa bu qiymatni ham qayta o'lchash kerak.
AUTO_PUBLISH_MIN_IMPORTANCE = int(os.getenv("AUTO_PUBLISH_MIN_IMPORTANCE", "2"))

# Muhim yangiliklarni Telegram kanalga avtomatik yuborish
AUTO_TELEGRAM = _bool("AUTO_TELEGRAM", "true")
AUTO_TELEGRAM_MIN_IMPORTANCE = int(os.getenv("AUTO_TELEGRAM_MIN_IMPORTANCE", "4"))
# Kanalga faqat yangi material ketsin: manba shundan oldin chiqargan maqola
# saytga chiqaveradi (arxiv va SEO uchun foydali), lekin kanalga yuborilmaydi.
# Yangi manba qo'shilganda uning arxivi kanalga to'kilib ketmasligi uchun ham
# kerak. 0 qilinsa cheklov o'chadi.
AUTO_TELEGRAM_MAX_AGE_HOURS = int(os.getenv("AUTO_TELEGRAM_MAX_AGE_HOURS", "48"))

# Rasm topilmaganda Gemini bilan generatsiya qilish (pullik — standart o'chiq)
IMAGE_GENERATION = _bool("IMAGE_GENERATION", "false")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
# Yaratilgan rasmlar saqlanadigan papka va ularning ommaviy manzili
MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")

# Frontend manzili (CORS uchun)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

# Saytning tahririy kuni va dayjest chegarasi shu vaqt zonasida hisoblanadi.
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Tashkent")
