import os
import unittest
from datetime import datetime, timezone

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_TIMEZONE"] = "Asia/Tashkent"

from app.routers.news import local_day_start_utc  # noqa: E402


class EditorialDayTests(unittest.TestCase):
    def test_tashkent_midnight_is_previous_day_1900_utc(self):
        now = datetime(2026, 8, 15, 21, 30, tzinfo=timezone.utc)

        self.assertEqual(local_day_start_utc(now), datetime(2026, 8, 15, 19, 0))

    def test_naive_input_is_treated_as_utc(self):
        now = datetime(2026, 8, 16, 3, 0)

        self.assertEqual(local_day_start_utc(now), datetime(2026, 8, 15, 19, 0))


if __name__ == "__main__":
    unittest.main()
