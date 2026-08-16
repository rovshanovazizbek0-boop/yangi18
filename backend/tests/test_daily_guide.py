import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("RUN_BACKGROUND_SERVICES", "false")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app.database import Base  # noqa: E402
from app.models import Article, Category, Guide  # noqa: E402
from app.services.daily_guide import (  # noqa: E402
    create_daily_guide,
    editorial_day_start_utc,
    evaluate_guide,
    normalize_guide,
)


def generated_response(title="ChatGPT yangi funksiyasidan xavfsiz foydalanish qo'llanmasi"):
    paragraph = (
        "Bu bo'lim foydalanuvchiga vazifani aniq belgilash, natijani asl manba "
        "bilan tekshirish va maxfiy ma'lumotni yubormaslik usulini amaliy misol "
        "orqali tushuntiradi. Javobdagi muhim faktlar alohida tekshiriladi. "
    )
    return {
        "title": title,
        "seo_title": "ChatGPT yangi funksiyasidan foydalanish bo'yicha qo'llanma",
        "description": (
            "ChatGPT yangi funksiyasini xavfsiz sinash, natijani tekshirish va amaliy "
            "ish jarayoniga qo'shishni o'rganing."
        ),
        "excerpt": (
            "Yangi imkoniyatni shunchaki yoqish emas, avval kichik vazifada sinash va "
            "natijani tekshirish kerak. Ushbu qo'llanma xavfsiz ish tartibini ko'rsatadi."
        ),
        "intro": (
            "AI vositasidagi yangi funksiya vaqtni tejashi mumkin, ammo natijani "
            "tekshirmasdan muhim ishga qo'llash xato xavfini oshiradi. Quyidagi ish "
            "jarayoni imkoniyatni kichik sinovdan boshlab nazorat bilan joriy etadi."
        ),
        "sections": [
            {
                "title": f"{index}. Amaliy bosqich va tekshiruv",
                "body": [paragraph, paragraph],
                "steps": ["Kichik vazifani tanlang", "Natijani tekshiring"],
                "example_label": "Sinov prompti" if index == 2 else "",
                "example_text": "Natijani jadvalda ber va noaniq faktni belgilagin." if index == 2 else "",
                "tip": "Maxfiy ma'lumot yubormang." if index == 3 else "",
            }
            for index in range(1, 5)
        ],
        "faq": [
            {"question": "Natijani tekshirish kerakmi?", "answer": "Ha, muhim faktlarni asl manbadan tekshiring."},
            {"question": "Maxfiy fayl yuborish mumkinmi?", "answer": "Ruxsatsiz maxfiy ma'lumotni yubormang."},
        ],
        "tags": ["ChatGPT", "AI", "Qo'llanma"],
        "duration_minutes": 14,
    }


class DailyGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()
        self.db.query(Guide).delete()
        self.db.query(Article).delete()
        self.db.query(Category).delete()
        category = Category(name="OpenAI", slug="openai")
        self.db.add(category)
        self.db.flush()
        self.category_id = category.id
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def add_article(self, *, suffix="1", importance=4, published_at=None):
        article = Article(
            title=f"OpenAI yangi AI funksiyasini taqdim etdi {suffix}",
            seo_title="OpenAI yangi funksiyasi",
            slug=f"openai-yangi-funksiya-{suffix}",
            summary="OpenAI foydalanuvchilar uchun yangi imkoniyatni taqdim etdi. " * 3,
            content="Yangi funksiya amaliy vazifalarni bajarishga yordam beradi. " * 20,
            practical_note="Foydalanuvchi avval kichik vazifada sinab ko'rishi kerak.",
            tags=["OpenAI", "ChatGPT", "AI"],
            importance=importance,
            original_title=f"OpenAI launches feature {suffix}",
            original_url=f"https://openai.com/news/feature-{suffix}",
            source_name="OpenAI Blog",
            category_id=self.category_id,
            status="published",
            published_at=published_at or datetime(2026, 8, 16, 8, 0),
        )
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def test_tashkent_day_starts_at_previous_1900_utc(self):
        result = editorial_day_start_utc(datetime(2026, 8, 16, 20, 0, tzinfo=timezone.utc))
        self.assertEqual(result, datetime(2026, 8, 16, 19, 0))

    @patch("app.services.daily_guide.generate_structured")
    def test_creates_only_one_guide_per_editorial_day(self, generate):
        source = self.add_article()
        generate.return_value = generated_response()
        now = datetime(2026, 8, 16, 10, 0, tzinfo=timezone.utc)

        first = create_daily_guide(self.db, now=now)
        second = create_daily_guide(self.db, now=now + timedelta(hours=2))

        self.assertEqual(first["status"], "created")
        self.assertEqual(second["status"], "already_created")
        generate.assert_called_once()
        guide = self.db.query(Guide).one()
        self.assertEqual(guide.source_article_id, source.id)
        self.assertEqual(guide.generation_type, "ai")
        self.assertEqual(guide.status, "published")
        self.assertEqual(guide.related_category_slug, "openai")

    @patch("app.services.daily_guide.generate_structured")
    def test_next_day_uses_a_different_source_article(self, generate):
        first_source = self.add_article(suffix="1", published_at=datetime(2026, 8, 16, 8, 0))
        generate.return_value = generated_response()
        first_now = datetime(2026, 8, 16, 10, 0, tzinfo=timezone.utc)
        create_daily_guide(self.db, now=first_now)

        second_source = self.add_article(suffix="2", published_at=datetime(2026, 8, 17, 8, 0))
        generate.return_value = generated_response("ChatGPT ikkinchi funksiyasi bo'yicha amaliy qo'llanma")
        second = create_daily_guide(self.db, now=first_now + timedelta(days=1))

        self.assertEqual(second["status"], "created")
        self.assertEqual(self.db.query(Guide).count(), 2)
        used = {guide.source_article_id for guide in self.db.query(Guide).all()}
        self.assertEqual(used, {first_source.id, second_source.id})

    def test_quality_gate_rejects_thin_content(self):
        source = self.add_article()
        candidate = normalize_guide({"title": "Juda qisqa", "sections": []})

        report = evaluate_guide(candidate, source)

        self.assertFalse(report.ok)
        self.assertTrue(any("bo'limlar" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
