from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


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

    @field_serializer("published_at", "created_at")
    def _as_utc(self, value: datetime | None) -> str | None:
        """Sanalarni vaqt zonasi bilan qaytaradi.

        Bazada UTC saqlanadi, lekin zonasiz. Zonasiz ISO qatorni JavaScript
        mahalliy vaqt deb o'qiydi — natijada saytda sana surilib ketadi va
        NewsArticle schema'sidagi datePublished Google uchun noaniq bo'ladi.
        """
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()


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
