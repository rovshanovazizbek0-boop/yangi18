import os
import unittest

os.environ["RUN_BACKGROUND_SERVICES"] = "false"
os.environ["AUTO_PUBLISH"] = "false"
os.environ["ADMIN_TOKEN"] = "1234567890123456789012345678901234567890"
os.environ["DATABASE_URL"] = "sqlite://"

from app.services.collector import _parse_feed

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


if __name__ == "__main__":
    unittest.main()
