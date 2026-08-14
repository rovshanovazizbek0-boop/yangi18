import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["AUTO_PUBLISH"] = "false"
os.environ["ADMIN_TOKEN"] = "1234567890123456789012345678901234567890"
os.environ["DATABASE_URL"] = "sqlite://"

from app.pipeline import format_error, is_fresh_for_channel


class ChannelFreshnessTests(unittest.TestCase):
    """Yangi manba qo'shilganda uning arxivi kanalga to'kilib ketmasligi kerak."""

    def test_recent_article_goes_to_channel(self):
        self.assertTrue(is_fresh_for_channel(datetime.utcnow() - timedelta(hours=3)))

    def test_old_article_is_held_back(self):
        self.assertFalse(is_fresh_for_channel(datetime.utcnow() - timedelta(days=30)))

    def test_boundary_is_inclusive(self):
        self.assertTrue(is_fresh_for_channel(datetime.utcnow() - timedelta(hours=47, minutes=59)))
        self.assertFalse(is_fresh_for_channel(datetime.utcnow() - timedelta(hours=48, minutes=1)))

    def test_unknown_date_is_allowed(self):
        """Sana bermaydigan manbalar bor — haqiqiy yangilikni yo'qotmaymiz."""
        self.assertTrue(is_fresh_for_channel(None))

    @patch("app.pipeline.AUTO_TELEGRAM_MAX_AGE_HOURS", 0)
    def test_zero_disables_the_limit(self):
        self.assertTrue(is_fresh_for_channel(datetime.utcnow() - timedelta(days=365)))


class ErrorRedactionTests(unittest.TestCase):
    def test_private_key_is_removed(self):
        message = 'File { "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvAIBAD" }'

        text = format_error(RuntimeError(message))

        self.assertNotIn("MIIEvAIBAD", text)
        self.assertNotIn("BEGIN PRIVATE KEY", text)

    def test_ordinary_error_is_untouched(self):
        text = format_error(RuntimeError("Barcha RSS manbalarini o'qish muvaffaqiyatsiz tugadi"))

        self.assertIn("Barcha RSS manbalarini", text)


if __name__ == "__main__":
    unittest.main()
