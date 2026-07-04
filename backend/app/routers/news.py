"""Ommaviy yangiliklar API — faqat chop etilgan maqolalar."""

from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Article, Category
from ..schemas import ArticleOut

router = APIRouter(prefix="/api/news", tags=["news"])


def published(db: Session):
    return db.query(Article).filter(Article.status == "published")


@router.get("", response_model=list[ArticleOut])
def latest_news(
    db: Session = Depends(get_db),
    kategoriya: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
):
    """Eng so'nggi yangiliklar (ixtiyoriy kategoriya filtri bilan)."""
    query = published(db)
    if kategoriya:
        query = query.join(Category).filter(Category.slug == kategoriya)
    return (
        query.order_by(Article.published_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/top", response_model=list[ArticleOut])
def top_news(db: Session = Depends(get_db), kunlar: int = 1, limit: int = Query(default=10, le=50)):
    """Top yangiliklar — muhimlik bahosi bo'yicha (standart: bugungi kun)."""
    since = datetime.utcnow() - timedelta(days=kunlar)
    return (
        published(db)
        .filter(Article.published_at >= since)
        .order_by(Article.importance.desc(), Article.published_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/digest", response_model=list[ArticleOut])
def daily_digest(db: Session = Depends(get_db)):
    """Bugungi AI dayjesti — bugun chop etilgan barcha yangiliklar."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return (
        published(db)
        .filter(Article.published_at >= today)
        .order_by(Article.importance.desc())
        .all()
    )


@router.get("/trends")
def trend_topics(db: Session = Depends(get_db), kunlar: int = 7, limit: int = 15):
    """Trend mavzular — so'nggi kunlardagi eng ko'p uchragan teglar."""
    since = datetime.utcnow() - timedelta(days=kunlar)
    articles = published(db).filter(Article.published_at >= since).all()
    counter = Counter(tag for a in articles for tag in (a.tags or []))
    return [{"teg": tag, "soni": count} for tag, count in counter.most_common(limit)]


@router.get("/search", response_model=list[ArticleOut])
def search_news(q: str, db: Session = Depends(get_db), limit: int = Query(default=20, le=100)):
    """Sarlavha, xulosa va matn bo'yicha qidiruv."""
    pattern = f"%{q}%"
    return (
        published(db)
        .filter(or_(
            Article.title.ilike(pattern),
            Article.summary.ilike(pattern),
            Article.content.ilike(pattern),
        ))
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/{slug}", response_model=ArticleOut)
def article_detail(slug: str, db: Session = Depends(get_db)):
    article = published(db).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=404, detail="Maqola topilmadi")
    return article
