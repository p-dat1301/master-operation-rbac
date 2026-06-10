from alembic import op
import sqlalchemy as sa


revision = "9b8d1a7c4e52"
down_revision = "c4f90b1a2e44"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "menus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("parent_key", sa.String(length=120), nullable=True),
        sa.Column("title_key", sa.String(length=180), nullable=False),
        sa.Column("route", sa.String(length=255), nullable=True),
        sa.Column("icon", sa.String(length=80), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("permission_key", sa.String(length=100), nullable=True),
        sa.Column("is_visible", sa.Boolean(), nullable=False),
        sa.Column("is_external", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["parent_key"], ["menus.key"]),
        sa.ForeignKeyConstraint(["permission_key"], ["permissions.code"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", name="uq_menu_key"),
        sa.UniqueConstraint("route", name="uq_menu_route"),
    )
    op.create_index("ix_menus_parent_key", "menus", ["parent_key"], unique=False)
    op.create_index("ix_menus_permission_key", "menus", ["permission_key"], unique=False)
    op.create_index("ix_menus_order", "menus", ["order"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_menus_order", table_name="menus")
    op.drop_index("ix_menus_permission_key", table_name="menus")
    op.drop_index("ix_menus_parent_key", table_name="menus")
    op.drop_table("menus")
