from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    seo_title: str
    slug: str
    summary: str
    content: str
    practical_note: str
    tags: list
    importance: int
    original_url: str
    source_name: str
    image_url: str | None
    category: CategoryOut | None
    status: str
    sent_to_telegram: bool
    published_at: datetime | None
    created_at: datetime


class ArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=12, max_length=300)
    seo_title: str | None = Field(default=None, min_length=12, max_length=300)
    summary: str | None = Field(default=None, min_length=40)
    content: str | None = Field(default=None, min_length=100)
    practical_note: str | None = Field(default=None, min_length=20)
    tags: list[str] | None = None
    importance: int | None = Field(default=None, ge=1, le=5)
    category_id: int | None = Field(default=None, gt=0)
    image_url: str | None = Field(default=None, max_length=1000)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned = []
        for tag in value:
            normalized = tag.strip()[:60]
            if normalized and normalized.casefold() not in {item.casefold() for item in cleaned}:
                cleaned.append(normalized)
        return cleaned[:6]


class StatsOut(BaseModel):
    jami: int
    kutilmoqda: int
    chop_etilgan: int
    rad_etilgan: int
    telegramga_yuborilgan: int
    kategoriyalar_boyicha: dict
