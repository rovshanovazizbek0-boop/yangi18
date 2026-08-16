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


class ToolSummaryOut(BaseModel):
    """Katalog ro'yxati uchun — og'ir matnlarsiz."""

    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    vendor: str
    tagline: str
    tool_category: str
    free_tier: bool | None
    uz: dict
    logo_url: str | None
    checked_at: datetime | None


class ToolOut(ToolSummaryOut):
    description: str
    plans: list
    alternatives: list
    official_url: str
    news_category_slug: str | None


class GuideSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    seo_title: str
    description: str
    excerpt: str
    provider: str
    difficulty: str
    duration_minutes: int
    tags: list
    related_category_slug: str | None
    generation_type: str
    source_article_id: int | None
    verified_at: datetime | None
    published_at: datetime | None
    updated_at: datetime

    @field_serializer("verified_at", "published_at", "updated_at")
    def _dates_as_utc(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()


class GuideOut(GuideSummaryOut):
    intro: str
    sections: list
    faq: list
    sources: list


class StatsOut(BaseModel):
    jami: int
    kutilmoqda: int
    chop_etilgan: int
    rad_etilgan: int
    telegramga_yuborilgan: int
    kategoriyalar_boyicha: dict
