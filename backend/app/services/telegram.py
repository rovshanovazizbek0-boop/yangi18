"""Telegram kanaliga post yuborish (Bot API orqali)."""

import html
import json

import httpx

from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, FRONTEND_ORIGIN
from ..models import Article

# Telegram sendPhoto uchun yuklanadigan fayl chegarasi.
MAX_PHOTO_BYTES = 10 * 1024 * 1024
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AINewsUZ/1.0; +https://aixabar.uz)"}


def _truncate(value: str | None, limit: int) -> str:
    text = " ".join((value or "").split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1].rstrip()}…"


def format_post(article: Article, *, compact: bool = False) -> str:
    title_limit = 160 if compact else 300
    summary_limit = 420 if compact else 1200
    practical_limit = 160 if compact else 500

    stars = "⭐" * max(1, min(5, article.importance))
    tags = " ".join(
        f"#{html.escape(_truncate(str(tag), 40).replace(' ', '_'))}"
        for tag in (article.tags or [])[:5]
    )
    category = _truncate(article.category.name if article.category else "AI", 80)
    return (
        f"<b>{html.escape(_truncate(article.title, title_limit))}</b>\n\n"
        f"{html.escape(_truncate(article.summary, summary_limit))}\n\n"
        f"💡 <i>{html.escape(_truncate(article.practical_note, practical_limit))}</i>\n\n"
        f"📂 {html.escape(category)} | Ahamiyati: {stars}\n"
        f"{tags}"
    )


def post_keyboard(article: Article) -> dict:
    """Post ostida katta va aniq Telegram inline tugmalarini qaytaradi."""
    rows = [[{
        "text": "📖 Batafsil o‘qish",
        "url": f"{FRONTEND_ORIGIN.rstrip('/')}/maqola/{article.slug}",
    }]]
    if article.original_url:
        rows.append([{
            "text": "🌐 Asl manba",
            "url": article.original_url,
        }])
    return {"inline_keyboard": rows}


def download_image(url: str) -> tuple[str, bytes, str] | None:
    """Rasmni o'zimiz yuklab olamiz: ba'zi CDN'lar (TechCrunch, The Verge)
    Telegram'ning fetcher'ini bloklaydi, bizning serverga esa ruxsat beradi.
    Yuklab bo'lmasa None qaytadi — u holda URL Telegram'ning o'ziga beriladi."""
    try:
        with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
            response = client.get(url)
            response.raise_for_status()
    except Exception:
        return None

    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    if not content_type.startswith("image/") or not (0 < len(response.content) <= MAX_PHOTO_BYTES):
        return None

    filename = url.split("?")[0].rstrip("/").split("/")[-1] or "image.jpg"
    return filename, response.content, content_type


def _send_photo(api: str, article: Article) -> str | None:
    """Rasmli post yuboradi; muvaffaqiyatsiz bo'lsa xato matnini qaytaradi."""
    fields = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "caption": format_post(article, compact=True),
        "parse_mode": "HTML",
    }
    keyboard = post_keyboard(article)
    image = download_image(article.image_url)
    try:
        if image:
            filename, content, content_type = image
            response = httpx.post(
                f"{api}/sendPhoto",
                data={**fields, "reply_markup": json.dumps(keyboard)},
                files={"photo": (filename, content, content_type)},
                timeout=60,
            )
        else:
            response = httpx.post(
                f"{api}/sendPhoto",
                json={**fields, "photo": article.image_url, "reply_markup": keyboard},
                timeout=30,
            )
        data = response.json()
    except Exception as error:
        return f"{type(error).__name__}: {error}"

    return None if data.get("ok") else str(data.get("description"))


def send_to_channel(article: Article) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN yoki TELEGRAM_CHANNEL_ID sozlanmagan")

    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    if article.image_url:
        error = _send_photo(api, article)
        if error is None:
            return
        # Rasm o'tmadi — post butunlay yo'qolmasligi uchun matn bilan davom etamiz.
        print(f"   ⚠ Rasmli post chiqmadi ({error}) — matnli post yuborilmoqda")

    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": format_post(article),
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
        "reply_markup": post_keyboard(article),
    }
    response = httpx.post(f"{api}/sendMessage", json=payload, timeout=30)

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram xatosi: {data.get('description')}")
