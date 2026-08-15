"""AI vositalari katalogi — ommaviy API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Tool
from ..schemas import ToolOut, ToolSummaryOut

router = APIRouter(prefix="/api/tools", tags=["tools"])


def published(db: Session):
    return db.query(Tool).filter(Tool.status == "published")


@router.get("", response_model=list[ToolSummaryOut])
def list_tools(db: Session = Depends(get_db), kategoriya: str | None = None):
    """Katalog ro'yxati (ixtiyoriy `kategoriya` filtri bilan)."""
    query = published(db)
    if kategoriya:
        query = query.filter(Tool.tool_category == kategoriya)
    return query.order_by(Tool.name).all()


@router.get("/kategoriyalar")
def tool_categories(db: Session = Depends(get_db)):
    """Katalogda haqiqatan mavjud bo'lgan kategoriyalar va ulardagi vositalar soni."""
    counts: dict[str, int] = {}
    for (category,) in published(db).with_entities(Tool.tool_category).all():
        counts[category] = counts.get(category, 0) + 1
    return [
        {"kategoriya": name, "soni": count}
        for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


@router.get("/{slug}", response_model=ToolOut)
def get_tool(slug: str, db: Session = Depends(get_db)):
    tool = published(db).filter(Tool.slug == slug).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Vosita topilmadi")
    return tool
