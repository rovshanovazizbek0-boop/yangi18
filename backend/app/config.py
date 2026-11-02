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

# Har tahririy kunda eng muhim, hali ishlatilmagan maqoladan bitta amaliy
# qo'llanma yaratish. Alohida quality gate sifatsiz natijani chop ettirmaydi.
AUTO_DAILY_GUIDE = _bool("AUTO_DAILY_GUIDE", "true")
DAILY_GUIDE_MIN_IMPORTANCE = int(os.getenv("DAILY_GUIDE_MIN_IMPORTANCE", "2"))
DAILY_GUIDE_LOOKBACK_HOURS = int(os.getenv("DAILY_GUIDE_LOOKBACK_HOURS", "72"))

# Rasm topilmaganda Gemini bilan generatsiya qilish (pullik — standart o'chiq)
IMAGE_GENERATION = _bool("IMAGE_GENERATION", "false")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
# Yaratilgan rasmlar saqlanadigan papka va ularning ommaviy manzili
MEDIA_DIR = os.getenv("MEDIA_DIR", "./media")
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")

# Frontend manzili (CORS uchun)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

# Har bir kategoriya uchun yuqori aniqlikdagi rasmiy zaxira muqova rasmlari
CATEGORY_DEFAULT_COVERS = {
    "openai": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80",
    "gemini": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
    "claude": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
    "xai": "https://images.unsplash.com/photo-1507499739999-097706ad8914?auto=format&fit=crop&w=1200&q=80",
    "meta": "https://images.unsplash.com/photo-1633419461186-7d40a38105ec?auto=format&fit=crop&w=1200&q=80",
    "deepseek": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80",
    "qwen": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
    "microsoft": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=80",
    "robototexnika": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1200&q=80",
    "dasturlash": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=80",
    "startuplar": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80",
}

# Saytning tahririy kuni va dayjest chegarasi shu vaqt zonasida hisoblanadi.
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Tashkent")
