"""Boshlang'ich categories, articles va tools sxemasi.

Revision ID: 20260816_01
Revises:
Create Date: 2026-08-16

Eski deploymentlar jadvallarni SQLAlchemy create_all bilan yaratgan. Shu sabab
migratsiya mavjud jadvalni qayta yaratmaydi, yangi bazada esa to'liq sxemani
yaratadi va keyingi revisionlar uchun barqaror baseline beradi.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260816_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = set(sa.inspect(bind).get_table_names())

    if "categories" not in existing:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("slug", sa.String(length=100), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
        op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)

    if "articles" not in existing:
        op.create_table(
            "articles",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=300), nullable=False),
            sa.Column("seo_title", sa.String(length=300), nullable=False),
            sa.Column("slug", sa.String(length=320), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("practical_note", sa.Text(), nullable=False),
            sa.Column("tags", sa.JSON(), nullable=False),
            sa.Column("importance", sa.Integer(), nullable=False),
            sa.Column("original_title", sa.String(length=500), nullable=False),
            sa.Column("original_url", sa.String(length=1000), nullable=False),
            sa.Column("source_name", sa.String(length=200), nullable=False),
            sa.Column("image_url", sa.String(length=1000), nullable=True),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("sent_to_telegram", sa.Boolean(), nullable=False),
            sa.Column("source_published_at", sa.DateTime(), nullable=True),
            sa.Column("published_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_articles_original_url", "articles", ["original_url"], unique=True)
        op.create_index("ix_articles_slug", "articles", ["slug"], unique=True)
        op.create_index("ix_articles_status", "articles", ["status"], unique=False)

    if "tools" not in existing:
        op.create_table(
            "tools",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=100), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("vendor", sa.String(length=100), nullable=False),
            sa.Column("tagline", sa.String(length=300), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("tool_category", sa.String(length=50), nullable=False),
            sa.Column("free_tier", sa.Boolean(), nullable=True),
            sa.Column("plans", sa.JSON(), nullable=False),
            sa.Column("uz", sa.JSON(), nullable=False),
            sa.Column("alternatives", sa.JSON(), nullable=False),
            sa.Column("official_url", sa.String(length=500), nullable=False),
            sa.Column("logo_url", sa.String(length=500), nullable=True),
            sa.Column("news_category_slug", sa.String(length=100), nullable=True),
            sa.Column("checked_at", sa.DateTime(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_tools_slug", "tools", ["slug"], unique=True)
        op.create_index("ix_tools_status", "tools", ["status"], unique=False)
        op.create_index("ix_tools_tool_category", "tools", ["tool_category"], unique=False)


def downgrade() -> None:
    # Baseline mavjud production jadvallarini ham qabul qilishi mumkin. Qaysi
    # jadvalni aynan shu revision yaratganini keyin bilib bo'lmaydi; avtomatik
    # downgrade ma'lumot yo'qotishi mumkin, shuning uchun ataylab bloklangan.
    raise RuntimeError("Boshlang'ich sxema downgrade qilinmaydi")
