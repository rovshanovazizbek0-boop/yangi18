"""Ishonchli manbalardan AI yangiliklarini yig'ish va dublikatlarni filtrlash.

RSS 2.0 va Atom formatlarini stdlib (xml.etree) bilan o'qiydi —
tashqi parser kutubxonalariga bog'liq emas.
"""

import html
import ipaddress
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import httpx
from sqlalchemy.orm import Session

from ..config import (
    ARTICLE_FETCH_WORKERS,
    DUPLICATE_LOOKBACK_DAYS,
    FETCH_FULL_ARTICLE,
    FULL_ARTICLE_MAX_CHARS,
    FULL_ARTICLE_MIN_SOURCE_CHARS,
)
from ..models import Article
from ..utils import title_hash, titles_semantically_similar

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


class _ParagraphExtractor(HTMLParser):
    """Maqoladagi <article><p> paragraflarini, bo'lmasa barcha <p>larni oladi."""

    _IGNORED = {"script", "style", "nav", "footer", "header", "aside", "form"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignored_depth = 0
        self.article_depth = 0
        self.current: list[str] | None = None
        self.current_in_article = False
        self.article_paragraphs: list[str] = []
        self.all_paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in self._IGNORED:
            self.ignored_depth += 1
        if tag == "article":
            self.article_depth += 1
        if tag == "p" and self.ignored_depth == 0:
            self.current = []
            self.current_in_article = self.article_depth > 0

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "p" and self.current is not None:
            paragraph = " ".join("".join(self.current).split())
            if len(paragraph) >= 40:
                self.all_paragraphs.append(paragraph)
                if self.current_in_article:
                    self.article_paragraphs.append(paragraph)
            self.current = None
        if tag == "article" and self.article_depth:
            self.article_depth -= 1
        if tag in self._IGNORED and self.ignored_depth:
            self.ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.ignored_depth == 0:
            self.current.append(data)


def _extract_article_text(page: str) -> str:
    parser = _ParagraphExtractor()
    try:
        parser.feed(page)
    except Exception:
        return ""
    paragraphs = parser.article_paragraphs or parser.all_paragraphs
    return "\n\n".join(paragraphs)[:FULL_ARTICLE_MAX_CHARS]


def _site_suffix(hostname: str | None) -> str:
    parts = (hostname or "").rstrip(".").lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else (hostname or "").lower()


def _same_site(url: str, feed_url: str) -> bool:
    return bool(_site_suffix(urlparse(url).hostname)) and (
        _site_suffix(urlparse(url).hostname) == _site_suffix(urlparse(feed_url).hostname)
    )


def _is_public_http_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
        return False
    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                parsed.hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        }
        return bool(addresses) and all(ipaddress.ip_address(address).is_global for address in addresses)
    except (OSError, ValueError):
        return False


def fetch_article_text(url: str, feed_url: str, client: httpx.Client) -> str:
    """Faqat o'sha public saytda qolgan redirectlardan maqola matnini oladi."""
    current = url
    for _ in range(4):
        if not _same_site(current, feed_url) or not _is_public_http_url(current):
            return ""
        try:
            response = client.get(current, follow_redirects=False)
        except Exception:
            return ""
        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("location")
            if not location:
                return ""
            current = urljoin(current, location)
            continue
        if response.status_code != 200:
            return ""
        if "html" not in response.headers.get("content-type", "").lower():
            return ""
        return _extract_article_text(response.text[:1_000_000])
    return ""


def _enrich_short_articles(items: list[dict]) -> None:
    if not FETCH_FULL_ARTICLE:
        return
    short = [item for item in items if len(item["content"]) < FULL_ARTICLE_MIN_SOURCE_CHARS]
    if not short:
        return

    def enrich(item: dict, client: httpx.Client) -> None:
        extracted = fetch_article_text(item["url"], item["_feed_url"], client)
        if len(extracted) >= max(800, len(item["content"]) + 200):
            item["content"] = extracted

    workers = max(1, min(ARTICLE_FETCH_WORKERS, 8))
    with httpx.Client(timeout=15, follow_redirects=False, headers=HEADERS) as client:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            list(executor.map(lambda item: enrich(item, client), short))


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)  # RFC 822 (RSS)
    except Exception:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))  # ISO (Atom)
        except Exception:
            return None

    # Bazada sanalar UTC, lekin timezone'siz saqlanadi. Offsetni shunchaki
    # olib tashlash vaqtni bir necha soatga surib yuboradi; avval UTC'ga o'tamiz.
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


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
    recent_since = datetime.utcnow() - timedelta(days=max(1, DUPLICATE_LOOKBACK_DAYS))
    recent_titles = [
        title for (title,) in db.query(Article.original_title).filter(
            Article.created_at >= recent_since
        ).all() if title
    ]

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
                print(f"  ERROR: Manba o'qilmadi ({feed['name']}): {error}")
                continue

            for entry in entries[:per_feed]:
                url, title = entry["url"], entry["title"]
                if not url or not title:
                    continue
                # Dublikat: URL yoki normallashtirilgan sarlavha bo'yicha
                if url in existing_urls or title_hash(title) in existing_hashes:
                    continue
                if any(titles_semantically_similar(title, old) for old in recent_titles):
                    continue

                fresh.append({
                    "title": title,
                    "content": entry["summary"][:6000],
                    "url": url,
                    "source": feed["name"],
                    "image_url": entry["image"],
                    "published_at": entry["published"],
                    "_feed_url": feed["url"],
                })
                existing_urls.add(url)
                existing_hashes.add(title_hash(title))
                recent_titles.append(title)

    if successful_feeds == 0:
        raise RuntimeError("Barcha RSS manbalarini o'qish muvaffaqiyatsiz tugadi")

    _enrich_short_articles(fresh)
    for item in fresh:
        item.pop("_feed_url", None)
    return fresh
