import unittest
from unittest.mock import Mock, patch

from app.services import ai_agent
from app.services.ai_agent import (
    ANALYSIS_SCHEMA,
    SYSTEM_PROMPT,
    _analyze_with_gemini,
    _extract_response_text,
    _google_schema,
    _validate,
    generate_structured,
)


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

    def test_custom_schema_gets_its_own_property_order(self):
        custom = {
            "type": "object",
            "properties": {"title": {"type": "string"}, "body": {"type": "string"}},
            "required": ["title", "body"],
            "additionalProperties": False,
        }

        result = _google_schema(custom)

        self.assertEqual(result["propertyOrdering"], ["title", "body"])
        self.assertNotIn("additionalProperties", result)

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

    @patch("app.services.ai_agent.GEMINI_API_KEY", "test-key")
    @patch("time.sleep")
    @patch("app.services.ai_agent.httpx.post")
    def test_gemini_retries_on_429_and_returns_parsed_json(self, http_post, _sleep):
        rate_limited = Mock(status_code=429, text="Resource exhausted")
        success = Mock(
            status_code=200,
            json=lambda: {
                "candidates": [{"content": {"parts": [{"text": '{"sarlavha": "Sinov"}'}]}}]
            },
        )
        http_post.side_effect = [rate_limited, success]

        result = _analyze_with_gemini("Test news")

        self.assertEqual(result, {"sarlavha": "Sinov"})
        self.assertEqual(http_post.call_count, 2)

    def test_extract_response_text_skips_thought_part(self):
        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"thought": True, "text": "ichki fikr"},
                            {"text": '{"sarlavha": "Haqiqiy"}'},
                        ]
                    }
                }
            ]
        }
        self.assertEqual(_extract_response_text(payload), '{"sarlavha": "Haqiqiy"}')

    @patch("app.services.ai_agent.GEMINI_API_KEY", "test-key")
    @patch("app.services.ai_agent.GEMINI_MODEL", "gemini-3.8-flash")
    @patch(
        "app.services.ai_agent.GEMINI_FALLBACK_MODELS",
        ("gemini-4-hydrogen", "gemini-3.5-flash-lite"),
    )
    @patch("app.services.ai_agent.httpx.post")
    def test_gemini_falls_back_to_next_model_on_503(self, http_post):
        calls = []

        def fake_post(url, **kwargs):
            calls.append(url)
            if "gemini-3.8-flash" in url:
                return Mock(status_code=503, text="High demand")
            return Mock(
                status_code=200,
                json=lambda: {
                    "candidates": [
                        {"content": {"parts": [{"text": '{"sarlavha": "Hydrogen javobi"}'}]}}
                    ]
                },
            )

        http_post.side_effect = fake_post
        result = _analyze_with_gemini("Test news")

        self.assertEqual(result, {"sarlavha": "Hydrogen javobi"})
        self.assertEqual(len(calls), 2)
        self.assertIn("gemini-3.8-flash", calls[0])
        self.assertIn("gemini-4-hydrogen", calls[1])

    def test_generate_structured_falls_back_from_vertex_to_gemini(self):
        with (
            patch.object(ai_agent, "AI_PROVIDER", "vertex"),
            patch.object(ai_agent, "GEMINI_API_KEY", "test-key"),
            patch.object(
                ai_agent,
                "_analyze_with_vertex",
                side_effect=RuntimeError("Vertex 403 billing"),
            ),
            patch.object(
                ai_agent,
                "_analyze_with_gemini",
                return_value={"sarlavha": "Gemini zaxira"},
            ) as gemini_mock,
        ):
            result = generate_structured(
                "Test",
                system_prompt="Sys",
                response_schema=ANALYSIS_SCHEMA,
            )

        gemini_mock.assert_called_once()
        self.assertEqual(result, {"sarlavha": "Gemini zaxira"})

    def test_generate_structured_reraises_vertex_error_without_gemini_key(self):
        with (
            patch.object(ai_agent, "AI_PROVIDER", "vertex"),
            patch.object(ai_agent, "GEMINI_API_KEY", ""),
            patch.object(
                ai_agent,
                "_analyze_with_vertex",
                side_effect=RuntimeError("Vertex 403 billing"),
            ),
        ):
            with self.assertRaises(RuntimeError):
                generate_structured(
                    "Test",
                    system_prompt="Sys",
                    response_schema=ANALYSIS_SCHEMA,
                )


if __name__ == "__main__":
    unittest.main()
