import json
import os
import unittest
from datetime import datetime, timezone

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["AUTO_PUBLISH"] = "false"
os.environ["ADMIN_TOKEN"] = "1234567890123456789012345678901234567890"
os.environ["DATABASE_URL"] = "sqlite://"

from app.schemas import ArticleOut

BASE = {
    "id": 1,
    "title": "Sinov maqolasi",
    "seo_title": "Sinov maqolasi",
    "slug": "sinov-maqolasi",
    "summary": "Qisqa xulosa.",
    "content": "Matn.",
    "practical_note": "Amaliy tavsiya.",
    "tags": ["AI"],
    "importance": 4,
    "original_url": "https://example.com/x",
    "source_name": "Test",
    "image_url": None,
    "category": None,
    "status": "published",
    "sent_to_telegram": False,
}


class ArticleDateSerializationTests(unittest.TestCase):
    """Sanalar zona bilan chiqishi shart — aks holda JavaScript ularni mahalliy
    vaqt deb o'qiydi va sayt sanasi hamda NewsArticle datePublished surilib ketadi."""

    def test_naive_dates_are_marked_utc(self):
        article = ArticleOut(
            **BASE,
            published_at=datetime(2026, 8, 14, 5, 29, 15, 196460),
            created_at=datetime(2026, 8, 14, 5, 29, 15, 197028),
        )

        data = json.loads(article.model_dump_json())

        self.assertEqual(data["published_at"], "2026-08-14T05:29:15.196460+00:00")
        self.assertEqual(data["created_at"], "2026-08-14T05:29:15.197028+00:00")

    def test_aware_dates_keep_their_offset(self):
        article = ArticleOut(
            **BASE,
            published_at=datetime(2026, 8, 14, 5, 29, 15, tzinfo=timezone.utc),
            created_at=datetime(2026, 8, 14, 5, 29, 15, tzinfo=timezone.utc),
        )

        self.assertEqual(
            json.loads(article.model_dump_json())["published_at"],
            "2026-08-14T05:29:15+00:00",
        )

    def test_missing_published_at_stays_null(self):
        article = ArticleOut(
            **BASE,
            published_at=None,
            created_at=datetime(2026, 8, 14, 5, 29, 15),
        )

        self.assertIsNone(json.loads(article.model_dump_json())["published_at"])


if __name__ == "__main__":
    unittest.main()
