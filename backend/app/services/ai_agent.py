"""AI Agent — inglizcha yangilikni o'zbek auditoriyasi uchun to'liq tayyorlaydi:
tarjima/moslashtirish, xulosa, SEO sarlavha, teglar, muhimlik bahosi, kategoriya.

Provayder .env orqali tanlanadi:
  AI_PROVIDER=gemini  (standart, GEMINI_API_KEY + GEMINI_MODEL)
  AI_PROVIDER=vertex  (Google ADC/service account + Vertex AI)
  AI_PROVIDER=claude  (ANTHROPIC_API_KEY + CLAUDE_MODEL)
"""

import json

import httpx

from ..config import (
    AI_PROVIDER,
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_CLOUD_PROJECT,
    VERTEX_GEMINI_MODEL,
)
from ..tags import normalize_tags

SYSTEM_PROMPT = """**Rol:** Sen sun'iy intellekt bo'yicha yetakchi o'zbek tahlilchisi va jurnalistisan.

**Vazifa:** Ingliz tilida berilgan AI yangiliklarini tahlil qilib, o'zbek auditoriyasi uchun ixcham, tushunarli va qadrli formatga o'tkazish.

**Qoidalar:**
0. **Faktlarga sodiqlik — eng muhim qoida:** Faqat berilgan sarlavha va matndagi ma'lumotlardan foydalan. Yetishmaydigan tafsilotni taxmin qilma, raqam yoki iqtibos to'qima. Bu qoida quyidagi hajm talablaridan ustun turadi: manbada ma'lumot yetarli bo'lmasa, to'ldirish uchun to'qima — qisqaroq yozganing ma'qul.
1. **Xulosa:** "xulosa" maydonida 4-6 jumlada, taxminan 400-700 belgi hajmida xulosa qil.
2. **To'liq maqola:** "maqola" maydonida yangilikni o'zbek tilida jurnalistik uslubda **kamida 5, ko'pi bilan 7 paragrafda** yorit; umumiy hajmi **2500 belgidan kam bo'lmasin** (manba imkon bergan darajada). Paragraflarni bo'sh qator bilan ajrat. Har paragraf yangi ma'lumot bersin — oldingi jumlani boshqa so'zlar bilan takrorlama.
3. **Baholash:** Avval "baho_sababi" maydonida bir jumlada yangilik qaysi daraja ta'rifiga
   mos kelishini ayt, so'ng "ahamiyati" maydonida 1 dan 5 gacha butun son ber.
   Shkala mutlaq: yangilikni o'z ichida emas, bir yillik AI yangiliklari oqimi bilan solishtir.
   - 5 — yilda bir necha marta bo'ladigan voqea: yetakchi modelning yangi avlodi,
     milliardlik sotib olish, butun tarmoqni o'zgartiradigan qaror yoki qonun
   - 4 — oyning eng muhim voqealaridan biri: yirik kompaniyaning yangi mahsuloti,
     e'tiborli tadqiqot natijasi, katta investitsiya yoki tarmoq miqyosidagi bahs
   - 3 — haftaning odatiy, lekin e'tiborga loyiq xabari: sezilarli yangi funksiya,
     muhim sud qarori, bozorga ta'sir qiluvchi qadam
   - 2 — kundalik oqim: kichik funksiya yoki yangilanish, narx o'zgarishi, hamkorlik
     e'loni, so'rovnoma natijasi, mish-mish, raqobatchining javobi
   - 1 — ahamiyatsiz: qo'llanma va hujjatlar, marketing materiali, fikr-mulohaza
     maqolasi, shaxsiy voqea yoki hazil, oldingi xabarning davomi
   Kunlik oqimning ko'pchiligi 1-3 darajaga tushadi — bu normal. 4 ni faqat yangilik
   haqiqatan o'sha oyning eng muhim voqealaridan biri bo'lsa qo'y, 5 ni esa deyarli
   hech qachon. Ikki daraja orasida ikkilansang, doim pastrog'ini tanla.
4. **Amaliy ahamiyat:** "amaliy_ahamiyat" maydonida ushbu yangilik dasturchilar yoki biznes egalari uchun qanday foyda yoki o'zgarish olib kelishini 1-2 jumlada tushuntir.
5. **SEO:** "seo_sarlavha" maydonida qidiruv tizimlari uchun optimallashtirilgan, kalit so'zlarga boy o'zbekcha sarlavha yoz (60-70 belgi atrofida).
6. **Teglar:** "teglar" maydonida 3-6 ta qisqa o'zbekcha teg ber.
7. **Kategoriyalash:** "kategoriya" maydonida yangilik qaysi yo'nalishga tegishli ekanini belgila.
8. **Tuzilma:** Javobni doim qat'iy JSON formatida qaytar."""

CATEGORY_SLUGS = [
    "openai", "gemini", "claude", "xai", "meta", "deepseek",
    "qwen", "microsoft", "startuplar", "robototexnika", "dasturlash",
]

# Kategoriya sluglari seed.py bilan mos bo'lishi shart.
# Maydonlar tartibi muhim: model ularni shu ketma-ketlikda yozadi, shuning
# uchun "ahamiyati" oxirida turadi — baho maqola yozib bo'lingandan keyin,
# undan oldingi "baho_sababi" bilan asoslanib qo'yiladi. "baho_sababi"
# saqlanmaydi; u faqat modelni raqamdan oldin o'ylashga majburlaydi.
ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "kategoriya": {"type": "string", "enum": CATEGORY_SLUGS},
        "sarlavha": {"type": "string"},
        "seo_sarlavha": {"type": "string"},
        "xulosa": {"type": "string"},
        "maqola": {"type": "string"},
        "amaliy_ahamiyat": {"type": "string"},
        "teglar": {"type": "array", "items": {"type": "string"}},
        "baho_sababi": {"type": "string"},
        "ahamiyati": {"type": "integer"},
    },
    "required": [
        "kategoriya", "sarlavha", "seo_sarlavha", "xulosa", "maqola",
        "amaliy_ahamiyat", "teglar", "baho_sababi", "ahamiyati",
    ],
    "additionalProperties": False,
}


def _google_schema() -> dict:
    """Gemini va Vertex uchun schema.

    `propertyOrdering` bo'lmasa Google modellari maydonlarni o'z bilganicha
    (ko'pincha alifbo tartibida) yozadi — unda "ahamiyati" eng birinchi
    chiqadi va baho maqola yozilishidan oldin qo'yiladi.
    """
    schema = {k: v for k, v in ANALYSIS_SCHEMA.items() if k != "additionalProperties"}
    schema["propertyOrdering"] = list(ANALYSIS_SCHEMA["properties"])
    return schema


def _validate(analysis: dict) -> dict:
    """Model javobini xavfsiz chegaralarga keltiradi."""
    analysis["ahamiyati"] = max(1, min(5, int(analysis.get("ahamiyati", 3))))
    if analysis.get("kategoriya") not in CATEGORY_SLUGS:
        analysis["kategoriya"] = "startuplar"
    # Teglar sayt bo'ylab yagona yozuvga keltiriladi, aks holda "Gemini" va
    # "gemini" alohida mavzu bo'lib ko'rinadi.
    analysis["teglar"] = normalize_tags(analysis.get("teglar"))
    return analysis


def _analyze_with_gemini(user_text: str) -> dict:
    """Gemini API (generateContent) — strukturali JSON javob bilan."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY sozlanmagan")

    # Gemini responseSchema OpenAPI kichik to'plami — additionalProperties kerak emas
    schema = _google_schema()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "maxOutputTokens": 8192,
        },
    }

    response = httpx.post(
        url,
        json=payload,
        headers={"x-goog-api-key": GEMINI_API_KEY},
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Gemini API xatosi {response.status_code}: {response.text[:300]}")

    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Gemini javobi kutilmagan formatda: {json.dumps(data)[:300]}")
    return json.loads(text)


_vertex_credentials = None
_vertex_project = ""


def _analyze_with_vertex(user_text: str) -> dict:
    """Vertex AI generateContent — ADC/service account bilan server autentifikatsiyasi."""
    global _vertex_credentials, _vertex_project

    import google.auth
    from google.auth.transport.requests import Request

    if _vertex_credentials is None:
        _vertex_credentials, detected_project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        _vertex_project = GOOGLE_CLOUD_PROJECT or detected_project or ""

    if not _vertex_project:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT aniqlanmadi")

    if not _vertex_credentials.valid:
        _vertex_credentials.refresh(Request())

    schema = _google_schema()
    url = (
        "https://aiplatform.googleapis.com/v1/projects/"
        f"{_vertex_project}/locations/{GOOGLE_CLOUD_LOCATION}/publishers/google/models/"
        f"{VERTEX_GEMINI_MODEL}:generateContent"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "maxOutputTokens": 8192,
        },
    }
    response = httpx.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {_vertex_credentials.token}"},
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Vertex AI xatosi {response.status_code}: {response.text[:300]}"
        )

    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Vertex AI javobi kutilmagan formatda: {json.dumps(data)[:300]}")
    return json.loads(text)


def _analyze_with_claude(user_text: str) -> dict:
    """Claude API — strukturali JSON javob bilan."""
    import anthropic  # ixtiyoriy provayder — faqat kerak bo'lganda import qilinadi

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY or None)
    schema = dict(ANALYSIS_SCHEMA)
    schema["properties"] = dict(schema["properties"])
    schema["properties"]["ahamiyati"] = {"type": "integer", "enum": [1, 2, 3, 4, 5]}

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        output_config={"format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": user_text}],
    )

    if response.stop_reason == "refusal":
        raise RuntimeError("Model tahlildan bosh tortdi (refusal)")

    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def active_model() -> str:
    """Hozir qaysi model ishlatilayotgani.

    analyze_news bilan bir xil shartlarni ishlatadi, shuning uchun /health
    dagi qiymat har doim haqiqatga mos bo'ladi — env bekor qilgan-qilmagani
    ham shundan ko'rinadi.
    """
    if AI_PROVIDER == "claude":
        return CLAUDE_MODEL
    if AI_PROVIDER == "vertex":
        return VERTEX_GEMINI_MODEL
    return GEMINI_MODEL


def analyze_news(title: str, content: str, url: str = "", source: str = "") -> dict:
    """Bitta yangilikni tahlil qilib, o'zbekcha tayyor maqola ma'lumotlarini qaytaradi."""
    user_text = f"Title: {title}\nSource: {source}\nURL: {url}\n\n{content}"

    if AI_PROVIDER == "claude":
        analysis = _analyze_with_claude(user_text)
    elif AI_PROVIDER == "vertex":
        analysis = _analyze_with_vertex(user_text)
    else:
        analysis = _analyze_with_gemini(user_text)

    return _validate(analysis)
