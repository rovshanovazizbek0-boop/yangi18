import os
import unittest
from datetime import datetime, timezone

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_TIMEZONE"] = "Asia/Tashkent"

from unittest.mock import patch

from app.routers.news import local_day_start_utc  # noqa: E402
from app.services.daily_guide import editorial_day_start_utc  # noqa: E402


class EditorialDayTests(unittest.TestCase):
    def test_tashkent_midnight_is_previous_day_1900_utc(self):
        now = datetime(2026, 8, 15, 21, 30, tzinfo=timezone.utc)

        self.assertEqual(local_day_start_utc(now), datetime(2026, 8, 15, 19, 0))
        self.assertEqual(editorial_day_start_utc(now), datetime(2026, 8, 15, 19, 0))

    def test_naive_input_is_treated_as_utc(self):
        now = datetime(2026, 8, 16, 3, 0)

        self.assertEqual(local_day_start_utc(now), datetime(2026, 8, 15, 19, 0))
        self.assertEqual(editorial_day_start_utc(now), datetime(2026, 8, 15, 19, 0))

    @patch("app.routers.news.ZoneInfo", side_effect=Exception("tzdata missing"))
    @patch("app.services.daily_guide.ZoneInfo", side_effect=Exception("tzdata missing"))
    def test_falls_back_to_utc_plus_5_when_zoneinfo_fails(self, _guide_tz, _news_tz):
        now = datetime(2026, 8, 15, 21, 30, tzinfo=timezone.utc)

        self.assertEqual(local_day_start_utc(now), datetime(2026, 8, 15, 19, 0))
        self.assertEqual(editorial_day_start_utc(now), datetime(2026, 8, 15, 19, 0))


if __name__ == "__main__":
    unittest.main()
