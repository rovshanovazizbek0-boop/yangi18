import unittest

from app.tags import canonical_tag, normalize_tags, tag_key


class TagKeyTests(unittest.TestCase):
    def test_case_and_apostrophes_are_ignored(self):
        self.assertEqual(tag_key("Sun'iy Intellekt"), tag_key("sun’iy intellekt"))

    def test_punctuation_is_ignored(self):
        self.assertEqual(tag_key("#Gemini!"), tag_key("gemini"))


class CanonicalTagTests(unittest.TestCase):
    def test_known_variants_collapse_to_one_spelling(self):
        for variant in ("gemini", "Gemini", "GEMINI", "google gemini"):
            self.assertEqual(canonical_tag(variant), "Gemini")

    def test_english_and_uzbek_names_of_one_topic_merge(self):
        self.assertEqual(canonical_tag("AI"), "Sun'iy intellekt")
        self.assertEqual(canonical_tag("artificial intelligence"), "Sun'iy intellekt")
        self.assertEqual(canonical_tag("Sun'iy Intellekt"), "Sun'iy intellekt")

    def test_unknown_tag_keeps_a_stable_spelling(self):
        self.assertEqual(canonical_tag("video generatsiya"), "Video generatsiya")
        self.assertEqual(canonical_tag("Video Generatsiya"), "Video generatsiya")

    def test_model_names_and_acronyms_survive(self):
        self.assertEqual(canonical_tag("GPT-5 narxi"), "GPT-5 narxi")
        self.assertEqual(canonical_tag("OpenAI"), "OpenAI")
        self.assertEqual(canonical_tag("xAI"), "xAI")

    def test_hash_prefix_and_spacing_are_cleaned(self):
        self.assertEqual(canonical_tag("  #anthropic  "), "Anthropic")

    def test_empty_tag_is_dropped(self):
        self.assertEqual(canonical_tag("   "), "")
        self.assertEqual(canonical_tag("#"), "")


class NormalizeTagsTests(unittest.TestCase):
    def test_duplicates_within_one_article_are_removed(self):
        self.assertEqual(
            normalize_tags(["AI", "sun'iy intellekt", "Gemini", "gemini"]),
            ["Sun'iy intellekt", "Gemini"],
        )

    def test_limit_applies_after_deduplication(self):
        tags = ["AI", "artificial intelligence", "a", "b", "c", "d", "e", "f"]
        self.assertEqual(len(normalize_tags(tags, limit=6)), 6)

    def test_empty_and_none_are_safe(self):
        self.assertEqual(normalize_tags(None), [])
        self.assertEqual(normalize_tags(["", "  ", "#"]), [])

    def test_non_string_values_do_not_crash(self):
        self.assertEqual(normalize_tags([5, "Gemini"]), ["5", "Gemini"])

    def test_result_is_idempotent(self):
        once = normalize_tags(["gemini", "AI", "video generatsiya"])
        self.assertEqual(normalize_tags(once), once)


if __name__ == "__main__":
    unittest.main()
