"""Add token_version to users for refresh-token revocation."""

from alembic import op
import sqlalchemy as sa

revision = "004_user_token_version"
down_revision = "003_partner_negotiations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )


def downgrade() -> None:
    op.drop_column("users", "token_version")
