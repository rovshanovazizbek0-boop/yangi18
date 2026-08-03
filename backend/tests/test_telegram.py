import os
import unittest
from unittest.mock import Mock, patch

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["AUTO_PUBLISH"] = "false"
os.environ["ADMIN_TOKEN"] = "1234567890123456789012345678901234567890"
os.environ["DATABASE_URL"] = "sqlite://"

from app.models import Article, Category
from app.services.telegram import format_post, post_keyboard, send_to_channel


class TelegramPostTests(unittest.TestCase):
    def setUp(self):
        self.article = Article(
            title="Telegram tugmalari sinovi",
            slug="telegram-tugmalari-sinovi",
            summary="Qisqa xulosa.",
            practical_note="Amaliy tavsiya.",
            tags=["AI", "Telegram"],
            importance=4,
            original_url="https://example.com/original",
            image_url="https://example.com/image.jpg",
            category=Category(name="AI Dasturlash", slug="ai-dasturlash"),
        )

    @patch("app.services.telegram.FRONTEND_ORIGIN", "https://aixabar.uz/")
    def test_keyboard_uses_separate_primary_and_source_rows(self):
        keyboard = post_keyboard(self.article)

        self.assertEqual(
            keyboard["inline_keyboard"],
            [
                [{
                    "text": "📖 Batafsil o‘qish",
                    "url": "https://aixabar.uz/maqola/telegram-tugmalari-sinovi",
                }],
                [{
                    "text": "🌐 Asl manba",
                    "url": "https://example.com/original",
                }],
            ],
        )

    def test_links_are_not_repeated_in_post_text(self):
        text = format_post(self.article, compact=True)

        self.assertNotIn("Asl manba", text)
        self.assertNotIn("Batafsil", text)

    @patch("app.services.telegram.TELEGRAM_BOT_TOKEN", "test-token")
    @patch("app.services.telegram.TELEGRAM_CHANNEL_ID", "@test-channel")
    @patch("app.services.telegram.httpx.post")
    def test_channel_photo_contains_inline_keyboard(self, http_post):
        http_post.return_value = Mock(json=lambda: {"ok": True})

        send_to_channel(self.article)

        payload = http_post.call_args.kwargs["json"]
        self.assertIn("reply_markup", payload)
        self.assertEqual(
            payload["reply_markup"]["inline_keyboard"][0][0]["text"],
            "📖 Batafsil o‘qish",
        )


if __name__ == "__main__":
    unittest.main()
