"""AI Agent quvuri: yig'ish -> dublikat filtri -> tahlil -> bazaga saqlash (pending).

Ishga tushirish:  python -m app.pipeline
Muntazam ishlashi uchun cron'ga qo'ying, masalan har soatda:
  0 * * * * cd /path/backend && python -m app.pipeline
"""

from .database import Base, SessionLocal, engine
from .models import Article, Category
from .seed import seed_categories
from .services.ai_agent import analyze_news
from .services.collector import collect_news
from .utils import slugify


def run_pipeline(per_feed: int = 5) -> int:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    saved = 0
    try:
        seed_categories(db)
        categories = {c.slug: c for c in db.query(Category).all()}

        print("📡 Yangiliklar yig'ilmoqda...")
        fresh = collect_news(db, per_feed=per_feed)
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
                print(f"   ✗ Tahlil xatosi: {error}")
                continue

            slug = slugify(analysis["sarlavha"])
            if db.query(Article).filter(Article.slug == slug).first():
                slug = f"{slug}-{saved + 1}"

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
                image_url=news["image_url"],
                category_id=categories.get(analysis["kategoriya"], None) and categories[analysis["kategoriya"]].id,
                source_published_at=news["published_at"],
                status="pending",
            )
            db.add(article)
            db.commit()
            saved += 1

        print(f"\n✅ {saved} ta maqola saqlandi (holati: pending — admin tasdig'ini kutmoqda).")
        return saved
    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline()
