"""Add owner_id to partners and create partner_negotiations table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_partner_negotiations"
down_revision = "002_donation_intents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "partners",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_table(
        "partner_negotiations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id", ondelete="CASCADE"), nullable=False),
        sa.Column("host_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("proposed_amount", sa.Float(), nullable=False),
        sa.Column("proposed_message", sa.Text(), nullable=True),
        sa.Column("contact_email", sa.String(), nullable=False),
        sa.Column("contact_phone", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("counter_amount", sa.Float(), nullable=True),
        sa.Column("counter_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("partner_negotiations")
    op.drop_column("partners", "owner_id")
