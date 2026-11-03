"""Articles jadvaliga views_count ustuni va default qiymat.

Revision ID: 20261103_01
Revises: 20260816_02
Create Date: 2026-11-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261103_01"
down_revision: Union[str, None] = "20260816_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    table_names = set(insp.get_table_names())
    if "articles" not in table_names:
        return

    columns = {c["name"] for c in insp.get_columns("articles")}
    if "views_count" not in columns:
        op.add_column(
            "articles",
            sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        )
    else:
        if bind.dialect.name != "sqlite":
            op.execute("UPDATE articles SET views_count = 0 WHERE views_count IS NULL")
            op.alter_column("articles", "views_count", server_default="0", nullable=False)


def downgrade() -> None:
    pass
