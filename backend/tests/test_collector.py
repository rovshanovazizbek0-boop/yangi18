import os
import unittest
from datetime import datetime

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["AUTO_PUBLISH"] = "false"
os.environ["ADMIN_TOKEN"] = "1234567890123456789012345678901234567890"
os.environ["DATABASE_URL"] = "sqlite://"

from app.services.collector import (
    _extract_article_text,
    _is_public_http_url,
    _parse_date,
    _parse_feed,
    _same_site,
)
from unittest.mock import patch

# The Verge/TechCrunch kabi WordPress manbalari URL'dagi & ni &#038; qilib beradi.
RSS_WITH_ENTITIES = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <item>
      <title>Suno Studio 2.0</title>
      <link>https://example.com/post?id=7&amp;#038;ref=rss</link>
      <description>&lt;img src="https://cdn.example.com/rasm.jpg?quality=90&amp;#038;strip=all" /&gt; matn</description>
    </item>
  </channel>
</rss>"""


class CollectorUrlTests(unittest.TestCase):
    def test_html_entities_are_decoded_in_urls(self):
        entry = _parse_feed(RSS_WITH_ENTITIES)[0]

        self.assertEqual(
            entry["image"],
            "https://cdn.example.com/rasm.jpg?quality=90&strip=all",
        )
        self.assertEqual(entry["url"], "https://example.com/post?id=7&ref=rss")

    def test_media_content_url_is_decoded(self):
        feed = RSS_WITH_ENTITIES.replace(
            "<description>",
            '<media:content url="https://cdn.example.com/a.jpg?w=1&amp;#038;h=2" /><description>',
        )

        self.assertEqual(
            _parse_feed(feed)[0]["image"],
            "https://cdn.example.com/a.jpg?w=1&h=2",
        )

    def test_source_timezone_is_converted_to_utc_before_becoming_naive(self):
        parsed = _parse_date("Sun, 16 Aug 2026 12:00:00 +0500")

        self.assertEqual(parsed, datetime(2026, 8, 16, 7, 0, 0))

    def test_article_extractor_prefers_article_paragraphs(self):
        page = """
        <nav><p>Bu navigatsiya matni yetarlicha uzun, lekin olinmasligi kerak.</p></nav>
        <article>
          <p>Birinchi asosiy paragraf qirq belgidan uzun va foydali ma'lumot beradi.</p>
          <p>Ikkinchi asosiy paragraf ham maqola matniga kiritilishi kerak bo'ladi.</p>
        </article>
        <footer><p>Bu footer matni ham natijaga aslo kirmasligi kerak.</p></footer>
        """

        text = _extract_article_text(page)

        self.assertIn("Birinchi asosiy", text)
        self.assertIn("Ikkinchi asosiy", text)
        self.assertNotIn("navigatsiya", text)
        self.assertNotIn("footer", text)

    def test_article_url_must_stay_on_the_feed_site(self):
        self.assertTrue(_same_site("https://www.example.com/news/1", "https://feeds.example.com/rss"))
        self.assertFalse(_same_site("https://attacker.test/news/1", "https://example.com/rss"))

    @patch("app.services.collector.socket.getaddrinfo")
    def test_private_ip_is_rejected(self, getaddrinfo):
        getaddrinfo.return_value = [(None, None, None, None, ("127.0.0.1", 443))]

        self.assertFalse(_is_public_http_url("https://example.com/article"))


if __name__ == "__main__":
    unittest.main()
