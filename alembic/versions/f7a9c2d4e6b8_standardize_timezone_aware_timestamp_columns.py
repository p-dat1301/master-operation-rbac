"""standardize timezone aware timestamp columns

Revision ID: f7a9c2d4e6b8
Revises: a4c2d8f1e9b6
Create Date: 2026-06-15 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "f7a9c2d4e6b8"
down_revision = "a4c2d8f1e9b6"
branch_labels = None
depends_on = None


_TIMESTAMP_COLUMNS: tuple[tuple[str, str, bool], ...] = (
    ("attendances", "check_in", False),
    ("attendances", "check_out", True),
    ("attendances", "created_at", False),
    ("audit_logs", "created_at", False),
    ("departments", "created_at", False),
    ("leave_balances", "created_at", False),
    ("leave_balances", "updated_at", False),
    ("leave_requests", "reviewed_at", True),
    ("leave_requests", "created_at", False),
    ("menus", "created_at", False),
    ("menus", "updated_at", False),
    ("notifications", "created_at", False),
    ("permissions", "created_at", False),
    ("roles", "created_at", False),
    ("tasks", "created_at", False),
    ("tasks", "updated_at", False),
    ("translations", "created_at", False),
    ("translations", "updated_at", False),
    ("users", "created_at", False),
)


def _upgrade_column(table_name: str, column_name: str, nullable: bool) -> None:
    op.alter_column(
        table_name,
        column_name,
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=nullable,
        postgresql_using=f"{column_name} AT TIME ZONE 'UTC'",
    )


def _downgrade_column(table_name: str, column_name: str, nullable: bool) -> None:
    op.alter_column(
        table_name,
        column_name,
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=nullable,
        postgresql_using=f"{column_name} AT TIME ZONE 'UTC'",
    )


def upgrade() -> None:
    for table_name, column_name, nullable in _TIMESTAMP_COLUMNS:
        _upgrade_column(table_name, column_name, nullable)


def downgrade() -> None:
    for table_name, column_name, nullable in reversed(_TIMESTAMP_COLUMNS):
        _downgrade_column(table_name, column_name, nullable)
