from sqlalchemy.orm import Session

from .models import Category

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
