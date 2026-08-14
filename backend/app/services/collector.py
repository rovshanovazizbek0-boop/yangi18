"""Ishonchli manbalardan AI yangiliklarini yig'ish va dublikatlarni filtrlash.

RSS 2.0 va Atom formatlarini stdlib (xml.etree) bilan o'qiydi —
tashqi parser kutubxonalariga bog'liq emas.
"""

import html
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx
from sqlalchemy.orm import Session

from ..models import Article
from ..utils import title_hash

FEEDS = [
    {"name": "OpenAI Blog", "url": "https://openai.com/news/rss.xml"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/"},
    # Google model e'lonlari (Gemini reliz'lari) technology/ai feed'iga tushmaydi —
    # ular quyidagi ikki manbada birinchi bo'lib chiqadi.
    {"name": "Google Gemini Blog", "url": "https://blog.google/products/gemini/rss/"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Ars Technica AI", "url": "https://arstechnica.com/ai/feed/"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
    {"name": "MIT Technology Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
]

ATOM = "{http://www.w3.org/2005/Atom}"
MEDIA = "{http://search.yahoo.com/mrss/}"
CONTENT_NS = "{http://purl.org/rss/1.0/modules/content/}"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AINewsUZ/1.0; +https://ainews.uz)"}


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).replace(tzinfo=None)  # RFC 822 (RSS)
    except Exception:
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)  # ISO (Atom)
    except Exception:
        return None


def _clean_url(value: str | None) -> str | None:
    """RSS ichidagi HTML entity'larni ochadi: `?a=1&#038;b=2` -> `?a=1&b=2`.
    Aks holda bunday URL Telegram va boshqa mijozlarda buzuq bo'ladi."""
    if not value:
        return None
    return html.unescape(value).strip() or None


def _first_image(item: ElementTree.Element, html_text: str) -> str | None:
    for tag in (f"{MEDIA}content", f"{MEDIA}thumbnail"):
        el = item.find(tag)
        if el is not None and el.get("url"):
            return _clean_url(el.get("url"))
    enclosure = item.find("enclosure")
    if enclosure is not None and str(enclosure.get("type", "")).startswith("image"):
        return _clean_url(enclosure.get("url"))
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_text or "")
    return _clean_url(match.group(1)) if match else None


def _parse_feed(xml_text: str) -> list[dict]:
    """RSS 2.0 yoki Atom hujjatidan yozuvlar ro'yxatini qaytaradi."""
    root = ElementTree.fromstring(xml_text)
    entries = []

    # RSS 2.0
    for item in root.iter("item"):
        raw_html = (
            (item.findtext(f"{CONTENT_NS}encoded") or item.findtext("description") or "")
        )
        entries.append({
            "title": (item.findtext("title") or "").strip(),
            "url": _clean_url(item.findtext("link")) or "",
            "summary": _strip_html(raw_html),
            "published": _parse_date(item.findtext("pubDate")),
            "image": _first_image(item, raw_html),
        })

    # Atom
    for entry in root.iter(f"{ATOM}entry"):
        link = ""
        for l in entry.findall(f"{ATOM}link"):
            if l.get("rel") in (None, "alternate"):
                link = l.get("href", "")
                break
        raw_html = entry.findtext(f"{ATOM}content") or entry.findtext(f"{ATOM}summary") or ""
        entries.append({
            "title": (entry.findtext(f"{ATOM}title") or "").strip(),
            "url": _clean_url(link) or "",
            "summary": _strip_html(raw_html),
            "published": _parse_date(
                entry.findtext(f"{ATOM}published") or entry.findtext(f"{ATOM}updated")
            ),
            "image": _first_image(entry, raw_html),
        })

    return entries


_OG_PATTERNS = [
    r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)(?::src)?["\'][^>]*content=["\']([^"\']+)["\']',
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\'](?:og:image|twitter:image)(?::src)?["\']',
]


def fetch_og_image(url: str) -> str | None:
    """Maqola sahifasidan og:image / twitter:image meta tegini oladi
    (RSS'da rasm bo'lmaganda zaxira usul)."""
    try:
        with httpx.Client(timeout=15, follow_redirects=True, headers=HEADERS) as client:
            page = client.get(url).text[:200_000]
    except Exception:
        return None
    for pattern in _OG_PATTERNS:
        match = re.search(pattern, page, re.IGNORECASE)
        if match:
            image_url = _clean_url(match.group(1))
            if image_url and image_url.startswith("http"):
                return image_url
    return None


def collect_news(db: Session, per_feed: int = 5) -> list[dict]:
    """RSS/Atom manbalardan yangi (bazada yo'q) yangiliklarni qaytaradi."""
    existing_urls = {u for (u,) in db.query(Article.original_url).all()}
    existing_hashes = {title_hash(t) for (t,) in db.query(Article.original_title).all()}

    fresh: list[dict] = []
    successful_feeds = 0
    with httpx.Client(timeout=20, follow_redirects=True, headers=HEADERS) as client:
        for feed in FEEDS:
            try:
                response = client.get(feed["url"])
                response.raise_for_status()
                entries = _parse_feed(response.text)
                successful_feeds += 1
            except Exception as error:
                print(f"  ✗ Manba o'qilmadi ({feed['name']}): {error}")
                continue

            for entry in entries[:per_feed]:
                url, title = entry["url"], entry["title"]
                if not url or not title:
                    continue
                # Dublikat: URL yoki normallashtirilgan sarlavha bo'yicha
                if url in existing_urls or title_hash(title) in existing_hashes:
                    continue

                fresh.append({
                    "title": title,
                    "content": entry["summary"][:6000],
                    "url": url,
                    "source": feed["name"],
                    "image_url": entry["image"],
                    "published_at": entry["published"],
                })
                existing_urls.add(url)
                existing_hashes.add(title_hash(title))

    if successful_feeds == 0:
        raise RuntimeError("Barcha RSS manbalarini o'qish muvaffaqiyatsiz tugadi")

    return fresh
