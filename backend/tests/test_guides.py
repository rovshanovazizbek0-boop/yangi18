import json
import os
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("RUN_BACKGROUND_SERVICES", "false")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import seed  # noqa: E402
from app.database import Base  # noqa: E402
from app.models import Guide  # noqa: E402
from app.routers.guides import get_guide, list_guides  # noqa: E402


GUIDE_ENTRY = {
    "slug": "chatgpt-prompt",
    "title": "ChatGPT uchun prompt yozish",
    "seo_title": "ChatGPT prompt qo'llanmasi",
    "description": "Qisqa va aniq SEO tavsif.",
    "excerpt": "Qo'llanmaning foydasini tushuntiradigan kirish matni.",
    "intro": "Batafsil kirish.",
    "sections": [{"title": "Birinchi qadam", "body": ["Tushuntirish."]}],
    "faq": [{"question": "Savol?", "answer": "Javob."}],
    "sources": [{"title": "Rasmiy manba", "url": "https://example.com/docs"}],
    "tags": ["ChatGPT", "Prompt"],
    "provider": "chatgpt",
    "difficulty": "boshlangich",
    "duration_minutes": 10,
    "related_category_slug": "openai",
    "position": 10,
    "tekshirilgan": "2026-08-16",
    "chop_etilgan_sana": "2026-08-16",
    "yangilangan": "2026-08-16",
}


class GuideTests(unittest.TestCase):
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
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def seed_from(self, entries):
        path = seed.GUIDES_FILE.with_name("guides_test.json")
        path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        with patch.object(seed, "GUIDES_FILE", path):
            return seed.seed_guides(self.db)

    def test_new_guide_starts_as_draft_and_is_hidden(self):
        self.assertEqual(self.seed_from([GUIDE_ENTRY]), 1)
        guide = self.db.query(Guide).one()
        self.assertEqual(guide.status, "draft")
        self.assertEqual(list_guides(db=self.db, limit=50), [])
        with self.assertRaises(HTTPException) as caught:
            get_guide(guide.slug, db=self.db)
        self.assertEqual(caught.exception.status_code, 404)

    def test_published_guide_is_listed_and_filterable(self):
        self.seed_from([{**GUIDE_ENTRY, "chop_etilgan": True}])

        self.assertEqual(
            [item.slug for item in list_guides(db=self.db, limit=50)],
            ["chatgpt-prompt"],
        )
        self.assertEqual(
            [item.slug for item in list_guides(db=self.db, provider="chatgpt", limit=50)],
            ["chatgpt-prompt"],
        )
        self.assertEqual(list_guides(db=self.db, provider="gemini", limit=50), [])
        self.assertEqual(
            [item.slug for item in list_guides(db=self.db, kategoriya="openai", limit=50)],
            ["chatgpt-prompt"],
        )

    def test_seed_is_idempotent_and_updates_content(self):
        published = {**GUIDE_ENTRY, "chop_etilgan": True}
        self.assertEqual(self.seed_from([published]), 1)
        self.assertEqual(self.seed_from([published]), 0)
        self.assertEqual(self.seed_from([{**published, "title": "Yangi sarlavha"}]), 1)
        self.assertEqual(self.db.query(Guide).one().title, "Yangi sarlavha")

    def test_real_seed_is_publishable_and_has_editorial_evidence(self):
        with seed.GUIDES_FILE.open(encoding="utf-8") as fh:
            entries = json.load(fh)

        self.assertGreaterEqual(len(entries), 5)
        self.assertEqual(len(entries), len({entry["slug"] for entry in entries}))
        for entry in entries:
            self.assertTrue(entry.get("chop_etilgan"), entry["slug"])
            self.assertGreaterEqual(len(entry.get("sections", [])), 4, entry["slug"])
            self.assertTrue(entry.get("tekshirilgan"), entry["slug"])
            self.assertTrue(entry.get("sources"), entry["slug"])
            for source in entry["sources"]:
                self.assertTrue(source["url"].startswith("https://"), entry["slug"])


if __name__ == "__main__":
    unittest.main()
