"""AI tayyorlagan maqolani saqlashdan oldingi editorial quality gate."""

from dataclasses import dataclass, field
import re
from urllib.parse import urlparse


_AI_PATTERN = re.compile(
    r"\b(?:ai|artificial intelligence|machine learning|deep learning|llm|"
    r"chatgpt|openai|anthropic|claude|gemini|grok|xai|deepseek|qwen|"
    r"neural|robot|sun['’ʻ]?iy intellekt)\b",
    re.IGNORECASE,
)

_ENGLISH_TITLE_WORDS = {
    "a", "after", "an", "and", "apps", "are", "ban", "block", "can",
    "denies", "for", "from", "in", "is", "judge", "just", "launches",
    "new", "of", "on", "request", "says", "seems", "the", "think", "to",
    "with", "will", "your",
}

_UZBEK_TITLE_WORDS = {
    "amalga", "bilan", "bozor", "degan", "emas", "haqida", "uchun",
    "intellekt", "mumkin", "nega", "qanday", "qildi", "qilmoqda",
    "taqdim", "tomonidan", "uning", "va", "yangi", "yaratdi",
}

_PROGRAMMING_PATTERN = re.compile(
    r"\b(?:api|code|coding|coder|developer|development|dastur|dasturlash|"
    r"github|programmer|software)\b",
    re.IGNORECASE,
)


@dataclass
class QualityReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _words(value: str) -> list[str]:
    return re.findall(r"[a-zA-Zʻ’']+", (value or "").lower())


def _looks_english(value: str) -> bool:
    words = _words(value)
    english_hits = sum(word.strip("'’ʻ") in _ENGLISH_TITLE_WORDS for word in words)
    uzbek_hits = sum(word.strip("'’ʻ") in _UZBEK_TITLE_WORDS for word in words)
    return english_hits >= 2 and english_hits > uzbek_hits


def evaluate_candidate(analysis: dict, source: dict) -> QualityReport:
    """Maqola publish/pending oqimiga kirishga yaroqliligini tekshiradi."""
    report = QualityReport()

    required_lengths = {
        "sarlavha": 12,
        "seo_sarlavha": 12,
        "xulosa": 80,
        "maqola": 300,
        "amaliy_ahamiyat": 35,
    }
    for field_name, minimum in required_lengths.items():
        value = str(analysis.get(field_name) or "").strip()
        if len(value) < minimum:
            report.errors.append(f"{field_name} juda qisqa ({len(value)}/{minimum})")

    title = str(analysis.get("sarlavha") or "").strip()
    if _looks_english(title):
        report.errors.append("sarlavha o'zbek tiliga moslashtirilmagan")

    source_text = " ".join(
        [str(source.get("title") or ""), str(source.get("content") or "")]
    )
    if not _AI_PATTERN.search(source_text):
        report.errors.append("asl material AI mavzusiga bevosita aloqador emas")

    original_url = str(source.get("url") or "")
    parsed_url = urlparse(original_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        report.errors.append("asl manba URL'i yaroqsiz")

    tags = analysis.get("teglar") or []
    if len(tags) < 3:
        report.warnings.append("teglar soni 3 tadan kam")

    combined = " ".join(
        [title, str(analysis.get("maqola") or ""), " ".join(map(str, tags))]
    )
    if analysis.get("kategoriya") == "dasturlash" and not _PROGRAMMING_PATTERN.search(combined):
        report.warnings.append("dasturlash kategoriyasi maqola mazmuniga mos kelmasligi mumkin")

    return report
