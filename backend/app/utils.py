import hashlib
import re


_TITLE_STOP_WORDS = {
    "about", "after", "and", "are", "for", "from", "has", "have", "how",
    "into", "its", "new", "now", "says", "that", "the", "their", "this",
    "to", "with", "will", "you", "your",
}


def slugify(text: str) -> str:
    """O'zbek lotin matnidan URL uchun slug yasaydi."""
    text = text.lower().replace("'", "").replace("ʻ", "").replace("’", "")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:200] or "maqola"


def title_hash(title: str) -> str:
    """Dublikatlarni aniqlash uchun normallashtirilgan sarlavha xeshi."""
    normalized = re.sub(r"[^a-z0-9]", "", title.lower())
    return hashlib.sha256(normalized.encode()).hexdigest()


def title_tokens(title: str) -> frozenset[str]:
    """Turli yozilgan, lekin bir voqeani bildiruvchi sarlavhalar uchun kalitlar."""
    words = re.findall(r"[a-z0-9]+", (title or "").lower())
    return frozenset(word for word in words if len(word) > 2 and word not in _TITLE_STOP_WORDS)


def titles_semantically_similar(left: str, right: str) -> bool:
    """Embedding talab qilmaydigan ehtiyotkor token-overlap filtri."""
    a, b = title_tokens(left), title_tokens(right)
    if min(len(a), len(b)) < 4:
        return False
    common = len(a & b)
    if common < 4:
        return False
    containment = common / min(len(a), len(b))
    jaccard = common / len(a | b)
    return containment >= 0.75 or jaccard >= 0.55
