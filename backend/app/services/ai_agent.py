"""AI Agent — inglizcha yangilikni o'zbek auditoriyasi uchun to'liq tayyorlaydi:
tarjima/moslashtirish, xulosa, SEO sarlavha, teglar, muhimlik bahosi, kategoriya."""

import json

import anthropic

from ..config import ANTHROPIC_API_KEY, CLAUDE_MODEL

SYSTEM_PROMPT = """**Rol:** Sen sun'iy intellekt bo'yicha yetakchi o'zbek tahlilchisi va jurnalistisan.

**Vazifa:** Ingliz tilida berilgan AI yangiliklarini tahlil qilib, o'zbek auditoriyasi uchun ixcham, tushunarli va qadrli formatga o'tkazish.

**Qoidalar:**
1. **Qisqalik:** "xulosa" maydonida asosiy ma'noni yo'qotmagan holda 3-5 jumlada xulosa qil.
2. **To'liq maqola:** "maqola" maydonida yangilikni o'zbek tilida 3-6 paragrafda to'liq, jurnalistik uslubda yorit. Paragraflarni bo'sh qator bilan ajrat.
3. **Baholash:** "ahamiyati" maydonida yangilikning ahamiyatiga qarab 1 dan 5 gacha butun son bilan baho ber.
4. **Amaliy ahamiyat:** "amaliy_ahamiyat" maydonida ushbu yangilik dasturchilar yoki biznes egalari uchun qanday foyda yoki o'zgarish olib kelishini 1-2 jumlada tushuntir.
5. **SEO:** "seo_sarlavha" maydonida qidiruv tizimlari uchun optimallashtirilgan, kalit so'zlarga boy o'zbekcha sarlavha yoz (60-70 belgi atrofida).
6. **Teglar:** "teglar" maydonida 3-6 ta qisqa o'zbekcha teg ber.
7. **Kategoriyalash:** "kategoriya" maydonida yangilik qaysi yo'nalishga tegishli ekanini belgila.
8. **Tuzilma:** Javobni doim qat'iy JSON formatida qaytar."""

# Kategoriya sluglari seed.py bilan mos bo'lishi shart.
ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "kategoriya": {
            "type": "string",
            "enum": [
                "openai", "gemini", "claude", "xai", "meta", "deepseek",
                "qwen", "microsoft", "startuplar", "robototexnika", "dasturlash",
            ],
        },
        "sarlavha": {"type": "string"},
        "seo_sarlavha": {"type": "string"},
        "xulosa": {"type": "string"},
        "maqola": {"type": "string"},
        "amaliy_ahamiyat": {"type": "string"},
        "teglar": {"type": "array", "items": {"type": "string"}},
        "ahamiyati": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
    },
    "required": [
        "kategoriya", "sarlavha", "seo_sarlavha", "xulosa",
        "maqola", "amaliy_ahamiyat", "teglar", "ahamiyati",
    ],
    "additionalProperties": False,
}

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY or None)
    return _client


def analyze_news(title: str, content: str, url: str = "", source: str = "") -> dict:
    """Bitta yangilikni tahlil qilib, o'zbekcha tayyor maqola ma'lumotlarini qaytaradi."""
    user_text = f"Title: {title}\nSource: {source}\nURL: {url}\n\n{content}"

    response = get_client().messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        output_config={"format": {"type": "json_schema", "schema": ANALYSIS_SCHEMA}},
        messages=[{"role": "user", "content": user_text}],
    )

    if response.stop_reason == "refusal":
        raise RuntimeError("Model tahlildan bosh tortdi (refusal)")

    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)
