from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    articles: Mapped[list["Article"]] = relationship(back_populates="category")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)

    # O'zbekcha kontent (AI agent tayyorlaydi)
    title: Mapped[str] = mapped_column(String(300))
    seo_title: Mapped[str] = mapped_column(String(300), default="")
    slug: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text, default="")           # qisqa xulosa
    content: Mapped[str] = mapped_column(Text, default="")           # to'liq maqola
    practical_note: Mapped[str] = mapped_column(Text, default="")    # "Bu nima degani?"
    tags: Mapped[list] = mapped_column(JSON, default=list)
    importance: Mapped[int] = mapped_column(Integer, default=3)      # 1-5

    # Asl manba
    original_title: Mapped[str] = mapped_column(String(500), default="")
    original_url: Mapped[str] = mapped_column(String(1000), unique=True, index=True)
    source_name: Mapped[str] = mapped_column(String(200), default="")
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category: Mapped[Category | None] = relationship(back_populates="articles")

    # Holat oqimi: pending -> published (admin tasdiqlagach) yoki rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    sent_to_telegram: Mapped[bool] = mapped_column(Boolean, default=False)

    source_published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Tool(Base):
    """AI vositalari katalogi.

    Maqolalardan farqli o'laroq bu ma'lumot AI tomonidan yozilmaydi: model
    "Uzcard ishlaydimi" degan savolga javob bilmaydi va to'qib qo'yadi.
    Katalogning butun qiymati `uz` maydonida — u qo'lda, sinab ko'rilgandan
    keyin to'ldiriladi. Tekshirilmagan qiymat `null` bo'lib qolishi kerak.
    """

    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    vendor: Mapped[str] = mapped_column(String(100), default="")
    tagline: Mapped[str] = mapped_column(String(300), default="")
    description: Mapped[str] = mapped_column(Text, default="")

    # matn | rasm | video | ovoz | kod | agent | qidiruv | tarjima | unumdorlik
    tool_category: Mapped[str] = mapped_column(String(50), index=True, default="matn")

    # None — hali tekshirilmagan. Saytda "noma'lum" bo'lib ko'rinadi.
    free_tier: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    # [{"nom": "Plus", "narx_usd": 20, "davr": "oy", "nimalar": [...]}]
    plans: Mapped[list] = mapped_column(JSON, default=list)
    # {"vpn_kerakmi": bool|null, "tolov": str|null, "tolov_yollari": [...],
    #  "ozbek_tili": {"baho": 1-5, "izoh": str}|null, "narx_somda": str|null}
    uz: Mapped[dict] = mapped_column(JSON, default=dict)
    alternatives: Mapped[list] = mapped_column(JSON, default=list)  # slug ro'yxati

    official_url: Mapped[str] = mapped_column(String(500), default="")
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Maqolalar bilan bog'lash uchun: qaysi yangilik kategoriyasiga tegishli
    news_category_slug: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # O'zbekiston ma'lumoti oxirgi marta qachon tekshirilgan — narxlar tez
    # eskiradi, shuning uchun sana sahifada ham ko'rsatiladi.
    checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="published", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
