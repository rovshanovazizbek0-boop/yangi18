"""AI'ni o'rganish bo'limi uchun ommaviy API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Guide
from ..schemas import GuideOut, GuideSummaryOut

router = APIRouter(prefix="/api/guides", tags=["guides"])


def published(db: Session):
    return db.query(Guide).filter(Guide.status == "published")


@router.get("", response_model=list[GuideSummaryOut])
def list_guides(
    db: Session = Depends(get_db),
    provider: str | None = None,
    kategoriya: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    query = published(db)
    if provider:
        query = query.filter(Guide.provider == provider)
    if kategoriya:
        query = query.filter(Guide.related_category_slug == kategoriya)
    # Kunlik AI darslar darhol bosh sahifada ko'rinishi uchun eng yangi
    # yangilangan qo'llanma birinchi; bir kunda seed qilingan darslar position
    # bo'yicha o'quv tartibini saqlaydi.
    return query.order_by(Guide.updated_at.desc(), Guide.position, Guide.title).limit(limit).all()


@router.get("/{slug}", response_model=GuideOut)
def get_guide(slug: str, db: Session = Depends(get_db)):
    guide = published(db).filter(Guide.slug == slug).first()
    if not guide:
        raise HTTPException(status_code=404, detail="Qo'llanma topilmadi")
    return guide
