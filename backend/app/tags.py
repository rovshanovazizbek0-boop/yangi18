"""Teglarni yagona kanonik ko'rinishga keltirish.

Teglarni model har safar erkin yozadi, shuning uchun bitta mavzu sayt bo'ylab
bir necha ko'rinishda paydo bo'ladi: "Gemini" / "gemini", "AI" / "sun'iy
intellekt". Trend ro'yxati ham ularni alohida sanaydi va bitta mavzu ikkiga
bo'linib ko'rinadi.

Shu sababdan teg ikki qismga ajratiladi:
  - kalit (`tag_key`) — solishtirish uchun; harf registri, apostrof va tinish
    belgilari hisobga olinmaydi;
  - ko'rinish (`canonical_tag`) — saytda chiqadigan yagona yozuv.
"""

import re

# Kanonik yozuv -> unga olib keladigan variantlar (kalit ko'rinishida: kichik
# harf, apostrofsiz). Kanonik yozuvning o'zi avtomatik qo'shiladi, shuning
# uchun ro'yxatda faqat undan farq qiladigan variantlar sanaladi.
# Bu yerga faqat haqiqatan bir xil mavzuni bildiruvchi variantlar kiritilsin.
_ALIAS_GROUPS: dict[str, tuple[str, ...]] = {
    "Sun'iy intellekt": ("ai", "artificial intelligence", "suniy intellekt texnologiyasi"),
    "OpenAI": ("open ai",),
    "ChatGPT": ("chat gpt",),
    "Google": ("google ai",),
    "Gemini": ("google gemini",),
    "Google DeepMind": ("deepmind",),
    "Anthropic": (),
    "Claude": ("claude ai",),
    "Meta AI": ("meta", "facebook ai"),
    "xAI": ("x ai",),
    "Grok": (),
    "DeepSeek": ("deep seek",),
    "Qwen": (),
    "Microsoft": ("microsoft ai",),
    "Copilot": ("github copilot",),
    "Nvidia": (),
    "LLM": ("large language model", "katta til modeli", "til modeli", "til modellari"),
    "AI agentlari": ("ai agent", "ai agenti", "ai agentlar", "agentlar"),
    "Neyron tarmoqlar": ("neyron tarmoq", "neural network", "neyron tarmoq"),
    "Mashinali o'qitish": ("machine learning", "mashinali organish"),
    "Robototexnika": ("robot", "robotlar", "robotics"),
    "Dasturlash": ("programming", "coding", "kod yozish"),
    "API": (),
    "Startuplar": ("startup", "startaplar", "startap"),
    "Investitsiya": ("investitsiyalar", "sarmoya", "moliyalashtirish"),
    "Texnologiya": ("texnologiyalar", "technology"),
    "Xavfsizlik": ("ai xavfsizligi", "security"),
    "Kiberxavfsizlik": ("cybersecurity",),
    "Tartibga solish": ("regulyatsiya", "qonunchilik", "regulation"),
    "Video generatsiya": ("video yaratish", "ai video"),
    "Rasm generatsiyasi": ("rasm yaratish", "image generation", "ai rasm"),
}

_APOSTROPHES = re.compile(r"['’ʼʻ`´]")
_NON_WORD = re.compile(r"[\W_]+", re.UNICODE)


def tag_key(tag: str) -> str:
    """Solishtirish kaliti: registr, apostrof va tinish belgilaridan xoli."""
    text = _APOSTROPHES.sub("", (tag or "").lower())
    return " ".join(_NON_WORD.sub(" ", text).split())


_ALIASES: dict[str, str] = {}
for _label, _variants in _ALIAS_GROUPS.items():
    _ALIASES[tag_key(_label)] = _label
    for _variant in _variants:
        _ALIASES[tag_key(_variant)] = _label


def _clean(tag: str) -> str:
    """Ortiqcha bo'shliq, boshidagi '#' va chetdagi tinish belgilarini oladi."""
    return " ".join((tag or "").strip().lstrip("#").strip(" .,:;!?-").split())


def _stable_case(tag: str) -> str:
    """Notanish teg uchun yozuv.

    Modelning katta harflari saqlanadi: teglar orasida atoqli otlar ko'p
    ("Sam Altman", "GPT-5", "OpenAI") va ularni kichik harfga tushirish nomni
    buzadi. Faqat butunlay kichik harfda kelgan teg bosh harfi bilan
    kattalashtiriladi.

    Bir tushunchaning ikki yozuvi ("Video generatsiya" va "Video Generatsiya")
    qolishi mumkin — ular `tag_key` bo'yicha baribir bitta guruhga tushadi,
    takrorlanadigan muhim nomlar esa `_ALIAS_GROUPS` da belgilangan.
    """
    if any(character.isupper() for character in tag):
        return tag
    return tag[:1].upper() + tag[1:]


def canonical_tag(tag: str) -> str:
    """Bitta tegning saytda ko'rinadigan yagona yozuvi. Bo'sh teg uchun ''."""
    cleaned = _clean(tag)
    if not cleaned:
        return ""
    return _ALIASES.get(tag_key(cleaned)) or _stable_case(cleaned)


def normalize_tags(tags, limit: int = 6) -> list[str]:
    """Teglar ro'yxatini kanonik ko'rinishga keltiradi.

    Bir maqolada bir mavzu ikki xil yozilgan bo'lsa ("AI" va "sun'iy
    intellekt"), birinchisi qoladi — shuning uchun chegara takrorlar
    tashlangandan keyin qo'llanadi.
    """
    result: list[str] = []
    seen: set[str] = set()
    for tag in tags or []:
        canonical = canonical_tag(str(tag))
        if not canonical:
            continue
        key = tag_key(canonical)
        if key in seen:
            continue
        seen.add(key)
        result.append(canonical)
    return result[:limit]
