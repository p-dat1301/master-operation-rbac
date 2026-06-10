from alembic import op
import sqlalchemy as sa


revision = "a4c2d8f1e9b6"
down_revision = "9b8d1a7c4e52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("key", sa.String(length=180), nullable=False),
        sa.Column("value", sa.String(length=500), nullable=False),
        sa.Column("namespace", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("locale", "key", name="uq_translation_locale_key"),
    )
    op.create_index("ix_translations_locale", "translations", ["locale"], unique=False)
    op.create_index("ix_translations_namespace", "translations", ["namespace"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_translations_namespace", table_name="translations")
    op.drop_index("ix_translations_locale", table_name="translations")
    op.drop_table("translations")
