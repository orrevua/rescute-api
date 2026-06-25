"""Add payment_link to donation_posts and create donation_intents table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_donation_intents"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("donation_posts", sa.Column("payment_link", sa.String(), nullable=True))
    op.create_table(
        "donation_intents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("donation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donation_posts.id"), nullable=False),
        sa.Column("donor_name", sa.String(), nullable=False),
        sa.Column("donor_email", sa.String(), nullable=False),
        sa.Column("donor_phone", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("donation_intents")
    op.drop_column("donation_posts", "payment_link")
