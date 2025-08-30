"""ensure optional user columns exist

Revision ID: f742ca1b099b
Revises: 001
Create Date: 2025-08-30 06:53:25.862634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f742ca1b099b'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: ensure optional user columns exist."""
    # Use raw SQL for IF NOT EXISTS to be idempotent on PostgreSQL
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(512),
        ADD COLUMN IF NOT EXISTS cover_photo_url VARCHAR(512),
        ADD COLUMN IF NOT EXISTS gender VARCHAR(20);
        """
    )


def downgrade() -> None:
    """Downgrade schema: drop optional columns (if present)."""
    op.execute(
        """
        ALTER TABLE users
        DROP COLUMN IF EXISTS gender,
        DROP COLUMN IF EXISTS cover_photo_url,
        DROP COLUMN IF EXISTS profile_photo_url;
        """
    )
