import json
import os
import unittest
from datetime import datetime
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("RUN_BACKGROUND_SERVICES", "false")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import seed  # noqa: E402
from app.database import Base  # noqa: E402
from app.models import Tool  # noqa: E402
from app.routers.tools import get_tool, list_tools, tool_categories  # noqa: E402

from fastapi import HTTPException  # noqa: E402


SEED_ENTRY = {
    "slug": "chatgpt",
    "name": "ChatGPT",
    "vendor": "OpenAI",
    "tagline": "Savolga javob beradi",
    "description": "Uzun tavsif.",
    "tool_category": "matn",
    "free_tier": None,
    "plans": [],
    "uz": {"vpn_kerakmi": None, "tolov": None},
    "alternatives": ["claude"],
    "official_url": "https://chatgpt.com",
    "news_category_slug": "openai",
}


class ToolSeedTests(unittest.TestCase):
    """Katalog fayldan yuklanadi va deploy'da yangilanib turadi."""

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
        self.db.query(Tool).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def seed_from(self, entries, tmp_name="tools_test.json"):
        path = seed.TOOLS_FILE.with_name(tmp_name)
        path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        with patch.object(seed, "TOOLS_FILE", path):
            return seed.seed_tools(self.db)

    def test_tools_are_created_from_the_file(self):
        self.assertEqual(self.seed_from([SEED_ENTRY]), 1)

        tool = self.db.query(Tool).one()
        self.assertEqual(tool.name, "ChatGPT")
        self.assertEqual(tool.alternatives, ["claude"])

    def test_new_tool_starts_as_draft(self):
        """To'ldirilmagan sahifa qidiruvga chiqmasin."""
        self.seed_from([SEED_ENTRY])

        self.assertEqual(self.db.query(Tool).one().status, "draft")

    def test_flag_publishes_and_hides_the_tool(self):
        self.seed_from([{**SEED_ENTRY, "chop_etilgan": True}])
        self.assertEqual(self.db.query(Tool).one().status, "published")

        self.assertEqual(self.seed_from([{**SEED_ENTRY, "chop_etilgan": False}]), 1)
        self.assertEqual(self.db.query(Tool).one().status, "draft")

    def test_second_seed_changes_nothing(self):
        self.seed_from([SEED_ENTRY])
        self.assertEqual(self.seed_from([SEED_ENTRY]), 0)

    def test_edited_file_updates_the_existing_tool(self):
        self.seed_from([SEED_ENTRY])
        edited = {**SEED_ENTRY, "uz": {"vpn_kerakmi": False, "tolov": "Xalqaro karta"}}

        self.assertEqual(self.seed_from([edited]), 1)
        self.assertEqual(self.db.query(Tool).one().uz["tolov"], "Xalqaro karta")

    def test_checked_date_is_read_from_the_file(self):
        self.seed_from([{**SEED_ENTRY, "tekshirilgan": "2026-08-15"}])

        self.assertEqual(self.db.query(Tool).one().checked_at, datetime(2026, 8, 15))

    def test_broken_date_does_not_break_the_seed(self):
        self.seed_from([{**SEED_ENTRY, "tekshirilgan": "kecha"}])

        self.assertIsNone(self.db.query(Tool).one().checked_at)

    def test_missing_file_is_not_an_error(self):
        with patch.object(seed, "TOOLS_FILE", seed.TOOLS_FILE.with_name("yoq.json")):
            self.assertEqual(seed.seed_tools(self.db), 0)

    def test_real_seed_file_is_valid(self):
        """Repodagi fayl har doim yuklanadigan holatda bo'lsin."""
        with seed.TOOLS_FILE.open(encoding="utf-8") as fh:
            entries = json.load(fh)

        self.assertGreater(len(entries), 0)
        slugs = [entry["slug"] for entry in entries]
        self.assertEqual(len(slugs), len(set(slugs)), "slug takrorlangan")
        for entry in entries:
            self.assertTrue(entry.get("name"), entry["slug"])
            self.assertTrue(entry.get("official_url", "").startswith("https://"), entry["slug"])


class ToolApiTests(unittest.TestCase):
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
        self.db.query(Tool).delete()
        self.db.add(Tool(slug="chatgpt", name="ChatGPT", tool_category="matn"))
        self.db.add(Tool(slug="midjourney", name="Midjourney", tool_category="rasm"))
        self.db.add(Tool(slug="qoralama", name="Qoralama", tool_category="matn", status="draft"))
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_drafts_stay_out_of_the_catalogue(self):
        slugs = [tool.slug for tool in list_tools(db=self.db)]

        self.assertEqual(slugs, ["chatgpt", "midjourney"])

    def test_category_filter(self):
        slugs = [tool.slug for tool in list_tools(db=self.db, kategoriya="rasm")]

        self.assertEqual(slugs, ["midjourney"])

    def test_category_counts_skip_drafts(self):
        self.assertEqual(
            tool_categories(db=self.db),
            [{"kategoriya": "matn", "soni": 1}, {"kategoriya": "rasm", "soni": 1}],
        )

    def test_draft_tool_is_not_reachable(self):
        with self.assertRaises(HTTPException) as caught:
            get_tool("qoralama", db=self.db)

        self.assertEqual(caught.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
