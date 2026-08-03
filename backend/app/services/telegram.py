"""Telegram kanaliga post yuborish (Bot API orqali)."""

import html

import httpx

from ..config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, FRONTEND_ORIGIN
from ..models import Article


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


def send_to_channel(article: Article) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN yoki TELEGRAM_CHANNEL_ID sozlanmagan")

    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    if article.image_url:
        text = format_post(article, compact=True)
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "photo": article.image_url,
            "caption": text,
            "parse_mode": "HTML",
            "reply_markup": post_keyboard(article),
        }
        response = httpx.post(f"{api}/sendPhoto", json=payload, timeout=30)
    else:
        text = format_post(article)
        payload = {
            "chat_id": TELEGRAM_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "reply_markup": post_keyboard(article),
        }
        response = httpx.post(f"{api}/sendMessage", json=payload, timeout=30)

    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram xatosi: {data.get('description')}")
