import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from .models import Category, Tool

TOOLS_FILE = Path(__file__).with_name("tools_seed.json")

# Fayldan bazaga ko'chiriladigan maydonlar. `status` bu ro'yxatda yo'q — u
# alohida, `chop_etilgan` bayrog'i orqali boshqariladi.
_TOOL_FIELDS = (
    "name", "vendor", "tagline", "description", "tool_category",
    "free_tier", "plans", "uz", "alternatives", "official_url",
    "logo_url", "news_category_slug",
)

# TZ bo'yicha kategoriyalar
CATEGORIES = [
    ("OpenAI", "openai"),
    ("Google Gemini", "gemini"),
    ("Anthropic (Claude)", "claude"),
    ("xAI (Grok)", "xai"),
    ("Meta AI", "meta"),
    ("DeepSeek", "deepseek"),
    ("Qwen", "qwen"),
    ("Microsoft AI", "microsoft"),
    ("AI Startuplar", "startuplar"),
    ("Robototexnika", "robototexnika"),
    ("AI Dasturlash", "dasturlash"),
]


def seed_categories(db: Session) -> None:
    existing = {slug for (slug,) in db.query(Category.slug).all()}
    for name, slug in CATEGORIES:
        if slug not in existing:
            db.add(Category(name=name, slug=slug))
    db.commit()


def _parse_date(value: str | None) -> datetime | None:
    """`"tekshirilgan": "2026-08-15"` qiymatini sanaga aylantiradi."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def seed_tools(db: Session) -> int:
    """Katalogni `tools_seed.json` dan yangilaydi; o'zgargan vositalar sonini qaytaradi.

    Kategoriyalardan farqli o'laroq bu yerda mavjud yozuvlar ham yangilanadi:
    hozircha fayl yagona manba, ya'ni katalogni to'ldirish = faylni tahrirlab
    deploy qilish. Admin panelida tahrirlash qo'shilganda buni qayta ko'rish
    kerak bo'ladi, aks holda deploy admin kiritgan ma'lumotni bosib ketadi.
    """
    if not TOOLS_FILE.exists():
        return 0

    with TOOLS_FILE.open(encoding="utf-8") as fh:
        entries = json.load(fh)

    existing = {tool.slug: tool for tool in db.query(Tool).all()}
    changed = 0

    for entry in entries:
        slug = entry.get("slug")
        if not slug:
            continue

        tool = existing.get(slug)
        is_new = tool is None
        if is_new:
            # Yangi vosita qoralama bo'lib tug'iladi: O'zbekiston ma'lumoti
            # to'ldirilmagan sahifa qidiruvga chiqishi kerak emas. Faylda
            # "chop_etilgan": true qilinganda ochiladi.
            tool = Tool(slug=slug, status="draft", created_at=datetime.utcnow())
            db.add(tool)

        dirty = is_new
        if "chop_etilgan" in entry:
            status = "published" if entry["chop_etilgan"] else "draft"
            if status != tool.status:
                tool.status = status
                dirty = True
        for field in _TOOL_FIELDS:
            if field in entry and getattr(tool, field, None) != entry[field]:
                setattr(tool, field, entry[field])
                dirty = True

        checked_at = _parse_date(entry.get("tekshirilgan"))
        if checked_at != tool.checked_at:
            tool.checked_at = checked_at
            dirty = True

        changed += dirty

    if changed:
        db.commit()
    return changed
