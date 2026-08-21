"""describe your change_03

Revision ID: cb1d1cd3e6b1
Revises: c255f0ca8b3d
Create Date: 2026-08-21 19:48:55.990172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb1d1cd3e6b1'
down_revision: Union[str, None] = 'c255f0ca8b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('full_name', sa.String(length=100), nullable=True)
    )

    op.execute("""
        UPDATE users
        SET full_name = TRIM(
            COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')
        )
    """)

    op.alter_column(
        'users',
        'full_name',
        existing_type=sa.String(length=100),
        nullable=False
    )

    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')


def downgrade() -> None:
    op.add_column(
        'users',
        sa.Column('first_name', sa.String(length=100), nullable=True)
    )

    op.add_column(
        'users',
        sa.Column('last_name', sa.String(length=100), nullable=True)
    )

    op.execute("""
        UPDATE users
        SET
            first_name = split_part(full_name, ' ', 1),
            last_name = NULLIF(
                TRIM(
                    SUBSTRING(
                        full_name
                        FROM LENGTH(split_part(full_name, ' ', 1)) + 1
                    )
                ),
                ''
            )
    """)

    op.alter_column(
        'users',
        'first_name',
        existing_type=sa.String(length=100),
        nullable=False
    )

    op.alter_column(
        'users',
        'last_name',
        existing_type=sa.String(length=100),
        nullable=False
    )

    op.drop_column('users', 'full_name')