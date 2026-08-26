"""add doctor working hours

Revision ID: a1c5b03e9f31
Revises: fb3a4a1e3bf8
Create Date: 2026-08-26 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1c5b03e9f31"
down_revision: Union[str, None] = "fb3a4a1e3bf8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doctor_working_hours",
        sa.Column("working_hours_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.String(length=5), nullable=False),
        sa.Column("end_time", sa.String(length=5), nullable=False),
        sa.CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_doctor_working_hours_day"),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctors.doctor_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("working_hours_id"),
        sa.UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_working_hours_doctor_day"),
    )
    op.create_index("ix_doctor_working_hours_working_hours_id", "doctor_working_hours", ["working_hours_id"])


def downgrade() -> None:
    op.drop_index("ix_doctor_working_hours_working_hours_id", table_name="doctor_working_hours")
    op.drop_table("doctor_working_hours")
