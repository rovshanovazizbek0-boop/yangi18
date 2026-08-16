import os
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("RUN_BACKGROUND_SERVICES", "false")
os.environ.setdefault("ADMIN_TOKEN", "1234567890123456789012345678901234567890")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from app import database  # noqa: E402
from app.pipeline import LAST_RUN  # noqa: E402


class HealthResponseTests(unittest.TestCase):
    """/health — deploy va sozlamalarni tekshirishning yagona oynasi."""

    @classmethod
    def setUpClass(cls):
        cls.previous_bind = database.SessionLocal.kw.get("bind")
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        database.Base.metadata.create_all(cls.engine)
        database.SessionLocal.configure(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        database.SessionLocal.configure(bind=cls.previous_bind)

    def body(self):
        from app.main import health

        return health()

    def test_database_is_reported(self):
        body = self.body()

        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["database"], "ok")

    def test_every_gate_that_can_hold_a_post_back_is_visible(self):
        publish = self.body()["publish"]

        for key in (
            "auto_publish",
            "auto_publish_min_importance",
            "auto_telegram",
            "auto_telegram_min_importance",
            "auto_telegram_max_age_hours",
            "auto_daily_guide",
            "daily_guide_min_importance",
            "daily_guide_lookback_hours",
        ):
            self.assertIn(key, publish)

    def test_pipeline_state_keeps_the_keys_the_workflow_reads(self):
        """keep-awake.yml jq bilan aynan shu yo'llarni o'qiydi."""
        pipeline = self.body()["pipeline"]

        self.assertIn("status", pipeline)
        self.assertIn("last_started_at", pipeline)
        self.assertIn("last_error", pipeline)
        self.assertIn("saved", pipeline["last_run"])
        self.assertIn("telegram_sent", pipeline["last_run"])
        self.assertIn("daily_guide_status", pipeline["last_run"])

    def test_active_model_is_reported(self):
        self.assertTrue(self.body()["pipeline"]["last_run"]["model"])
        self.assertIn("provider", LAST_RUN)


if __name__ == "__main__":
    unittest.main()
