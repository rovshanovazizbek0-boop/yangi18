import unittest

from app.utils import title_tokens, titles_semantically_similar


class SemanticTitleTests(unittest.TestCase):
    def test_near_duplicate_event_is_detected(self):
        left = "Google lets users remove visible watermarks from AI generated media"
        right = "Google users can now remove visible AI watermarks from generated media"

        self.assertTrue(titles_semantically_similar(left, right))

    def test_different_company_news_is_not_merged(self):
        left = "Google launches a new Gemini coding model for developers"
        right = "Meta invests billions in a new data center in Texas"

        self.assertFalse(titles_semantically_similar(left, right))

    def test_generic_short_titles_are_not_merged(self):
        self.assertFalse(titles_semantically_similar("New AI model", "New AI model"))

    def test_stop_words_are_removed(self):
        self.assertNotIn("the", title_tokens("The new model for developers"))


if __name__ == "__main__":
    unittest.main()
