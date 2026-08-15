import unittest

from app.services.ai_agent import ANALYSIS_SCHEMA, SYSTEM_PROMPT, _google_schema, _validate


class SchemaOrderTests(unittest.TestCase):
    """Maydonlar tartibi kalibrlashning bir qismi — baho eng oxirida qo'yiladi."""

    def test_score_is_generated_last(self):
        order = _google_schema()["propertyOrdering"]

        self.assertEqual(order[-1], "ahamiyati")
        self.assertEqual(order[-2], "baho_sababi")
        self.assertLess(order.index("maqola"), order.index("ahamiyati"))

    def test_ordering_covers_every_field(self):
        self.assertEqual(
            sorted(_google_schema()["propertyOrdering"]),
            sorted(ANALYSIS_SCHEMA["properties"]),
        )

    def test_google_schema_drops_unsupported_keyword(self):
        self.assertNotIn("additionalProperties", _google_schema())

    def test_prompt_states_the_whole_scale(self):
        for level in ("1 —", "2 —", "3 —", "4 —", "5 —"):
            self.assertIn(level, SYSTEM_PROMPT)


class ValidationTests(unittest.TestCase):
    def test_score_is_clamped_to_the_scale(self):
        self.assertEqual(_validate({"ahamiyati": 9})["ahamiyati"], 5)
        self.assertEqual(_validate({"ahamiyati": 0})["ahamiyati"], 1)

    def test_missing_score_falls_back_to_the_middle(self):
        self.assertEqual(_validate({})["ahamiyati"], 3)

    def test_unknown_category_falls_back(self):
        self.assertEqual(_validate({"kategoriya": "yo'q-kategoriya"})["kategoriya"], "startuplar")

    def test_tags_are_normalized(self):
        self.assertEqual(_validate({"teglar": ["gemini", "AI"]})["teglar"], ["Gemini", "Sun'iy intellekt"])


if __name__ == "__main__":
    unittest.main()
