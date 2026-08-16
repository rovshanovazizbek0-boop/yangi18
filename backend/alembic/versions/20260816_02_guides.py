"""AI o'rganish qo'llanmalari jadvali.

Revision ID: 20260816_02
Revises: 20260816_01
Create Date: 2026-08-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260816_02"
down_revision: Union[str, None] = "20260816_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if "guides" in set(sa.inspect(bind).get_table_names()):
        return

    op.create_table(
        "guides",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("seo_title", sa.String(length=240), nullable=False),
        sa.Column("description", sa.String(length=320), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("intro", sa.Text(), nullable=False),
        sa.Column("sections", sa.JSON(), nullable=False),
        sa.Column("faq", sa.JSON(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("difficulty", sa.String(length=30), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("related_category_slug", sa.String(length=100), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("generation_type", sa.String(length=20), nullable=False),
        sa.Column("source_article_id", sa.Integer(), nullable=True),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["source_article_id"], ["articles.id"]),
    )
    op.create_index("ix_guides_provider", "guides", ["provider"], unique=False)
    op.create_index("ix_guides_slug", "guides", ["slug"], unique=True)
    op.create_index("ix_guides_status", "guides", ["status"], unique=False)
    op.create_index(
        "ix_guides_source_article_id",
        "guides",
        ["source_article_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_guides_source_article_id", table_name="guides")
    op.drop_index("ix_guides_status", table_name="guides")
    op.drop_index("ix_guides_slug", table_name="guides")
    op.drop_index("ix_guides_provider", table_name="guides")
    op.drop_table("guides")
