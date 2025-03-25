"""Fix created_at type for accounts table

Revision ID: b4e03153b58d
Revises: 07b140577523
Create Date: 2025-03-25 08:52:06.134244

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b4e03153b58d"
down_revision: Union[str, None] = "07b140577523"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "accounts",
        "created_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at::timestamp with time zone",
    )


def downgrade():
    op.alter_column(
        "accounts",
        "created_at",
        type_=sa.String(),
        postgresql_using="created_at::varchar",
    )
