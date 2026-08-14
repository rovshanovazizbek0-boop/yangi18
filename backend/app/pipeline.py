"""AI Agent quvuri: yig'ish -> dublikat filtri -> tahlil -> saqlash.

AUTO_PUBLISH=true bo'lsa maqolalar darhol saytga chiqadi va
muhimlari (AUTO_TELEGRAM_MIN_IMPORTANCE dan yuqori) Telegram kanalga
avtomatik yuboriladi. Xavfsiz standart AUTO_PUBLISH=false: maqolalar
quality gate'dan o'tib, pending holatda admin tasdig'ini kutadi.

Ishga tushirish:  python -m app.pipeline
Muntazam ishlashi uchun cron'ga qo'ying, masalan har soatda:
  0 * * * * cd /path/backend && .venv/bin/python -m app.pipeline
"""

import re
from datetime import datetime

from .config import (
    AI_PROVIDER,
    AUTO_PUBLISH,
    AUTO_PUBLISH_MIN_IMPORTANCE,
    AUTO_TELEGRAM,
    AUTO_TELEGRAM_MIN_IMPORTANCE,
    IMAGE_GENERATION,
    TELEGRAM_BOT_TOKEN,
)
from .database import Base, SessionLocal, engine
from .models import Article, Category
from .seed import seed_categories
from .services.ai_agent import analyze_news
from .services.collector import collect_news, fetch_og_image
from .services.image_gen import generate_image
from .services.quality import evaluate_candidate
from .services.telegram import send_to_channel
from .utils import slugify

# Oxirgi ishga tushirish tafsilotlari — /health orqali ko'rinadi, shuning uchun
# server loglariga kirmasdan ham nima yiqilganini bilish mumkin.
LAST_RUN: dict = {
    "provider": AI_PROVIDER,
    "collected": None,
    "saved": None,
    "analysis_errors": None,
    "quality_rejected": None,
    "telegram_sent": None,
    "last_analysis_error": None,
    "last_telegram_error": None,
}


# Xato matnida maxfiy ma'lumot bo'lishi mumkin: masalan
# GOOGLE_APPLICATION_CREDENTIALS ga yo'l o'rniga JSON kalit qo'yilsa,
# google-auth butun kalitni xato matniga qo'shib yuboradi. /health esa ochiq
# endpoint — shuning uchun tashqariga chiqishdan oldin tozalanadi.
_SECRET_MARKERS = ('"private_key"', "-----BEGIN", "PRIVATE KEY")
_SECRET_PATTERNS = [
    re.compile(r"\b(?:gho_|ghp_|github_pat_|sk-ant-|sk-|AIza)[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{30,}"),  # Telegram bot tokeni
]


def redact_secrets(text: str) -> str:
    """Maxfiy qiymatlarni xato matnidan olib tashlaydi."""
    cut = min((i for i in (text.find(m) for m in _SECRET_MARKERS) if i != -1), default=-1)
    if cut != -1:
        text = f"{text[:cut]}<maxfiy ma'lumot olib tashlandi>"
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("<maxfiy>", text)
    return text


def format_error(error: BaseException, limit: int = 300) -> str:
    """Xatoni bitta qatorga jamlaydi (JSON javobiga qo'yish uchun)."""
    text = redact_secrets(" ".join(f"{type(error).__name__}: {error}".split()))
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


def run_pipeline(per_feed: int = 5) -> int:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    saved = 0
    collected = 0
    analysis_errors = 0
    quality_rejected = 0
    telegram_sent = 0
    LAST_RUN.update({
        "provider": AI_PROVIDER,
        "collected": 0,
        "saved": 0,
        "analysis_errors": 0,
        "quality_rejected": 0,
        "telegram_sent": 0,
        "last_analysis_error": None,
        "last_telegram_error": None,
    })
    try:
        seed_categories(db)
        categories = {c.slug: c for c in db.query(Category).all()}

        print("📡 Yangiliklar yig'ilmoqda...")
        fresh = collect_news(db, per_feed=per_feed)
        collected = len(fresh)
        print(f"   {len(fresh)} ta yangi yangilik topildi.")

        for i, news in enumerate(fresh, 1):
            print(f"🤖 [{i}/{len(fresh)}] {news['title'][:65]}")
            try:
                analysis = analyze_news(
                    title=news["title"],
                    content=news["content"],
                    url=news["url"],
                    source=news["source"],
                )
            except Exception as error:
                analysis_errors += 1
                LAST_RUN["last_analysis_error"] = format_error(error)
                print(f"   ✗ Tahlil xatosi: {error}")
                continue

            quality = evaluate_candidate(analysis, news)
            for warning in quality.warnings:
                print(f"   ⚠ Quality warning: {warning}")
            if not quality.ok:
                quality_rejected += 1
                print(f"   ✗ Quality gate rad etdi: {'; '.join(quality.errors)}")
                continue

            slug = slugify(analysis["sarlavha"])
            if db.query(Article).filter(Article.slug == slug).first():
                slug = f"{slug}-{saved + 1}"

            auto_publish = AUTO_PUBLISH and analysis["ahamiyati"] >= AUTO_PUBLISH_MIN_IMPORTANCE

            # Rasm zanjiri: RSS -> maqola sahifasidan og:image -> (ixtiyoriy) Gemini
            image_url = news["image_url"] or fetch_og_image(news["url"])
            if not image_url and IMAGE_GENERATION:
                image_url = generate_image(analysis["sarlavha"], slug)
                if image_url:
                    print("   ✓ Rasm generatsiya qilindi")

            article = Article(
                title=analysis["sarlavha"],
                seo_title=analysis["seo_sarlavha"],
                slug=slug,
                summary=analysis["xulosa"],
                content=analysis["maqola"],
                practical_note=analysis["amaliy_ahamiyat"],
                tags=analysis["teglar"],
                importance=analysis["ahamiyati"],
                original_title=news["title"],
                original_url=news["url"],
                source_name=news["source"],
                image_url=image_url,
                category_id=categories.get(analysis["kategoriya"], None) and categories[analysis["kategoriya"]].id,
                source_published_at=news["published_at"],
                status="published" if auto_publish else "pending",
                published_at=datetime.utcnow() if auto_publish else None,
            )
            db.add(article)
            db.commit()
            saved += 1

            if auto_publish:
                print("   ✓ Saytga chiqarildi")

            # Muhim yangiliklarni Telegram kanalga avtomatik yuborish
            if (
                auto_publish
                and AUTO_TELEGRAM
                and TELEGRAM_BOT_TOKEN
                and analysis["ahamiyati"] >= AUTO_TELEGRAM_MIN_IMPORTANCE
            ):
                try:
                    send_to_channel(article)
                    article.sent_to_telegram = True
                    db.commit()
                    telegram_sent += 1
                    print("   ✓ Telegram kanalga yuborildi")
                except Exception as error:
                    LAST_RUN["last_telegram_error"] = format_error(error)
                    print(f"   ✗ Telegram xatosi: {error}")

        if fresh and saved == 0 and analysis_errors == len(fresh):
            raise RuntimeError("Barcha yangi yangiliklar AI tahlilida xatoga uchradi")

        mode = "saytga chiqarildi (avto)" if AUTO_PUBLISH else "pending — admin tasdig'ini kutmoqda"
        print(
            f"\n✅ {saved} ta maqola saqlandi ({mode}). "
            f"Quality gate rad etdi: {quality_rejected}."
        )
        return saved
    finally:
        # Xato bilan tugasa ham hisoblagichlar /health uchun yangilanadi.
        LAST_RUN.update({
            "collected": collected,
            "saved": saved,
            "analysis_errors": analysis_errors,
            "quality_rejected": quality_rejected,
            "telegram_sent": telegram_sent,
        })
        db.close()


if __name__ == "__main__":
    run_pipeline()
