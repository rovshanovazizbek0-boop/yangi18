import unittest

from app.services.quality import evaluate_candidate


def valid_analysis(**overrides):
    data = {
        "kategoriya": "openai",
        "sarlavha": "OpenAI yangi sun'iy intellekt modelini taqdim etdi",
        "seo_sarlavha": "OpenAI yangi sun'iy intellekt modelini taqdim etdi",
        "xulosa": "OpenAI yangi modelini taqdim etdi. Model tezroq ishlaydi va foydalanuvchilar uchun yangi imkoniyatlar yaratadi.",
        "maqola": "OpenAI yangi sun'iy intellekt modelini taqdim etdi. " * 20,
        "amaliy_ahamiyat": "Bu yangilanish dasturchilar va bizneslar uchun ish jarayonlarini tezlashtirishi mumkin.",
        "teglar": ["OpenAI", "sun'iy intellekt", "model"],
        "ahamiyati": 4,
    }
    data.update(overrides)
    return data


def valid_source(**overrides):
    data = {
        "title": "OpenAI launches a new artificial intelligence model",
        "content": "The AI model adds new reasoning and developer capabilities.",
        "url": "https://openai.com/news/example",
    }
    data.update(overrides)
    return data


class QualityGateTests(unittest.TestCase):
    def test_accepts_relevant_uzbek_article(self):
        report = evaluate_candidate(valid_analysis(), valid_source())
        self.assertTrue(report.ok, report.errors)

    def test_rejects_untranslated_english_title(self):
        report = evaluate_candidate(
            valid_analysis(sarlavha="Judge denies request to block new AI apps"),
            valid_source(),
        )
        self.assertIn("sarlavha o'zbek tiliga moslashtirilmagan", report.errors)

    def test_rejects_non_ai_source(self):
        report = evaluate_candidate(
            valid_analysis(),
            valid_source(
                title="This nine dollar key blocks addictive apps",
                content="A physical NFC key helps people reduce screen time.",
            ),
        )
        self.assertIn("asl material AI mavzusiga bevosita aloqador emas", report.errors)

    def test_warns_about_suspicious_programming_category(self):
        report = evaluate_candidate(
            valid_analysis(kategoriya="dasturlash"),
            valid_source(),
        )
        self.assertTrue(report.ok)
        self.assertTrue(any("dasturlash" in warning for warning in report.warnings))


if __name__ == "__main__":
    unittest.main()
