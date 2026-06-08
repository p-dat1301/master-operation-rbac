"""attendance datetime and persistence fix

Revision ID: c4f90b1a2e44
Revises: 388ec37210d1
Create Date: 2026-06-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "c4f90b1a2e44"
down_revision = "388ec37210d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("attendances", sa.Column("total_minutes", sa.Integer(), nullable=True))
    op.add_column("attendances", sa.Column("ip_address", sa.String(length=45), nullable=True))
    op.alter_column(
        "attendances",
        "check_in",
        existing_type=sa.Time(),
        type_=sa.DateTime(),
        nullable=False,
        postgresql_using="date + check_in",
    )
    op.alter_column(
        "attendances",
        "check_out",
        existing_type=sa.Time(),
        type_=sa.DateTime(),
        nullable=True,
        postgresql_using="date + check_out",
    )


def downgrade() -> None:
    op.alter_column(
        "attendances",
        "check_out",
        existing_type=sa.DateTime(),
        type_=sa.Time(),
        nullable=True,
        postgresql_using="check_out::time",
    )
    op.alter_column(
        "attendances",
        "check_in",
        existing_type=sa.DateTime(),
        type_=sa.Time(),
        nullable=True,
        postgresql_using="check_in::time",
    )
    op.drop_column("attendances", "ip_address")
    op.drop_column("attendances", "total_minutes")
