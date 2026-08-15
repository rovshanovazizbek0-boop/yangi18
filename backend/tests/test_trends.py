import os
import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("RUN_BACKGROUND_SERVICES", "false")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app.backfill import backfill_tags  # noqa: E402
from app.database import Base  # noqa: E402
from app.models import Article  # noqa: E402
from app.routers.news import trend_topics  # noqa: E402


class TagAggregationTests(unittest.TestCase):
    """Bir mavzu turlicha yozilgan bo'lsa ham trend ro'yxatida bitta bo'lishi kerak."""

    @classmethod
    def setUpClass(cls):
        # Boshqa test modullariga tegmaslik uchun alohida engine va sessiya.
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()
        self.db.query(Article).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def add_article(self, slug: str, tags: list[str]):
        self.db.add(Article(
            title=f"Sinov maqolasi {slug}",
            slug=slug,
            original_url=f"https://example.com/{slug}",
            tags=tags,
            status="published",
            published_at=datetime.utcnow(),
        ))
        self.db.commit()

    def test_spelling_variants_count_as_one_topic(self):
        for i, tag in enumerate(["gemini", "Gemini", "GEMINI"]):
            self.add_article(f"gemini-{i}", [tag])

        self.assertEqual(trend_topics(db=self.db), [{"teg": "Gemini", "soni": 3}])

    def test_aliases_of_one_topic_merge(self):
        for i, tag in enumerate(["AI", "sun'iy intellekt", "Artificial Intelligence"]):
            self.add_article(f"ai-{i}", [tag])

        self.assertEqual(trend_topics(db=self.db), [{"teg": "Sun'iy intellekt", "soni": 3}])

    def test_pending_articles_stay_out_of_trends(self):
        self.add_article("chop-etilgan", ["Gemini"])
        self.db.add(Article(
            title="Tasdiq kutayotgan maqola",
            slug="kutmoqda",
            original_url="https://example.com/kutmoqda",
            tags=["Gemini"],
            status="pending",
        ))
        self.db.commit()

        self.assertEqual(trend_topics(db=self.db), [{"teg": "Gemini", "soni": 1}])


class BackfillTests(unittest.TestCase):
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
        self.db.query(Article).delete()
        self.db.add(Article(
            title="Eski teglar bilan maqola",
            slug="eski-teglar",
            original_url="https://example.com/eski",
            tags=["gemini", "AI", "sun'iy intellekt", "#startap"],
            status="published",
            published_at=datetime.utcnow(),
        ))
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_existing_tags_are_rewritten(self):
        self.assertEqual(backfill_tags(self.db), 1)

        article = self.db.query(Article).one()
        self.assertEqual(article.tags, ["Gemini", "Sun'iy intellekt", "Startuplar"])

    def test_second_run_changes_nothing(self):
        backfill_tags(self.db)
        self.assertEqual(backfill_tags(self.db), 0)


if __name__ == "__main__":
    unittest.main()
