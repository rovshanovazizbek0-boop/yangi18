"""Bazadagi eski teglarni kanonik ko'rinishga keltiradi.

Yangi maqolalarga normallashtirish saqlash paytida qo'llanadi (`app.tags`),
lekin undan oldin yozilganlar eski yozuvda qoladi va trend ro'yxati baribir
bo'linib ko'rinadi. Shu funksiya jarayon ishga tushganda bir marta ishlaydi;
o'zgarishi kerak bo'lgan qatorlar qolmagach, u faqat o'qiydi.

Qo'lda ishga tushirish:  python -m app.backfill
"""

from sqlalchemy.orm import Session

from .models import Article
from .tags import normalize_tags


def backfill_tags(db: Session) -> int:
    """Teglari kanonik bo'lmagan maqolalarni yangilaydi; o'zgargan soni qaytadi."""
    changed = 0
    for article in db.query(Article).all():
        current = list(article.tags or [])
        canonical = normalize_tags(current)
        if canonical != current:
            article.tags = canonical
            changed += 1
    if changed:
        db.commit()
    return changed


if __name__ == "__main__":
    from .database import SessionLocal

    session = SessionLocal()
    try:
        print(f"{backfill_tags(session)} ta maqola tegi yangilandi.")
    finally:
        session.close()
