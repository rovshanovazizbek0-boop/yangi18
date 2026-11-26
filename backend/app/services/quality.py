"""AI tayyorlagan maqolani saqlashdan oldingi editorial quality gate."""

from dataclasses import dataclass, field
import re
from urllib.parse import urlparse


from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Article
from ..tags import normalize_tags


_AI_PATTERN = re.compile(
    r"\b(?:ai|artificial intelligence|machine learning|deep learning|llm|"
    r"chatgpt|openai|anthropic|claude|gemini|grok|xai|deepseek|qwen|"
    r"neural|robot|sun['’ʻ]?iy intellekt)\b",
    re.IGNORECASE,
)

_ENGLISH_TITLE_WORDS = {
    "a", "about", "achieves", "after", "agent", "agents", "an", "and",
    "announces", "apps", "are", "ban", "block", "brings", "builds", "can",
    "creates", "denies", "detects", "for", "from", "gets", "helps", "how",
    "human", "in", "into", "is", "its", "judge", "just", "launches", "level",
    "makes", "model", "models", "more", "new", "now", "of", "on", "over",
    "releases", "request", "says", "seems", "sense", "shows", "smell", "the",
    "think", "to", "uses", "using", "what", "why", "will", "with", "your",
}

TEXT_REPLACEMENTS = (
    ("Â«", "«"),
    ("Â»", "»"),
    ("â€™", "’"),
    ("â€œ", "“"),
    ("â€ ", "”"),
    ("â€“", "–"),
    ("â€”", "—"),
    ("deepfakt", "dipfeyk"),
    ("Deepfakt", "Dipfeyk"),
)

_NAME_PATTERNS = (
    (re.compile(r"\b(?:Jensen Xuang|Jensen Xuan|Jyensen Xuang|Jensen Huang)\b", re.IGNORECASE), "Jensen Huang"),
    (re.compile(r"\b(?:Sem Oltman|Sam Oltman)\b", re.IGNORECASE), "Sam Altman"),
    (re.compile(r"\bIlan Mask\b", re.IGNORECASE), "Ilon Mask"),
    (re.compile(r"\bMark Sukerberg\b", re.IGNORECASE), "Mark Tsukerberg"),
)


def normalize_text(value: str | None) -> str:
    """Kodlash (mojibake), atama va shaxs nomlari imlosini birxillashtiradi."""
    text = str(value or "")
    for broken, fixed in TEXT_REPLACEMENTS:
        text = text.replace(broken, fixed)
    for pattern, canonical in _NAME_PATTERNS:
        text = pattern.sub(canonical, text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def normalize_analysis(analysis: dict) -> dict:
    """AI javobidagi barcha matn maydonlari va teglarni kanonik shaklga keltiradi."""
    for key in ("sarlavha", "seo_sarlavha", "xulosa", "maqola", "amaliy_ahamiyat"):
        if key in analysis:
            analysis[key] = normalize_text(analysis.get(key))
    if "teglar" in analysis:
        analysis["teglar"] = normalize_tags(normalize_text(t) for t in (analysis.get("teglar") or []))
    return analysis


def cleanup_existing_articles(db: Session) -> tuple[int, int]:
    """Mavjud maqolalardagi kodlash/nom xatolarini tuzatadi va tarjimasiz inglizcha maqolalarni yashiradi."""
    corrected = 0
    for field in (
        Article.title,
        Article.seo_title,
        Article.summary,
        Article.content,
        Article.practical_note,
    ):
        for broken, fixed in TEXT_REPLACEMENTS:
            corrected += (
                db.query(Article)
                .filter(field.contains(broken))
                .update({field: func.replace(field, broken, fixed)}, synchronize_session=False)
            )
    for article in db.query(Article).all():
        changed = False
        for attr in ("title", "seo_title", "summary", "content", "practical_note"):
            raw = getattr(article, attr)
            if raw:
                cleaned = normalize_text(raw)
                if cleaned != raw:
                    setattr(article, attr, cleaned)
                    changed = True
        if changed:
            corrected += 1

    hidden = 0
    for article in db.query(Article).filter(Article.status == "published").all():
        if _looks_english(article.title):
            article.status = "rejected"
            hidden += 1

    db.commit()
    return hidden, corrected

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
