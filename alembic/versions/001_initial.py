"""Create Rescute's initial schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def _id_column() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table("users", _id_column(), sa.Column("email", sa.String(), nullable=False, unique=True), sa.Column("hashed_password", sa.String(), nullable=False), sa.Column("role", sa.String(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()))
    op.create_table("protector_profiles", _id_column(), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True), sa.Column("org_name", sa.String(), nullable=False), sa.Column("description", sa.Text()), sa.Column("phone", sa.String()), sa.Column("city", sa.String()), sa.Column("state", sa.String()))
    op.create_table("foster_profiles", _id_column(), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True), sa.Column("full_name", sa.String(), nullable=False), sa.Column("phone", sa.String(), nullable=False), sa.Column("city", sa.String(), nullable=False), sa.Column("state", sa.String(), nullable=False))
    op.create_table("cats", _id_column(), sa.Column("protector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("name", sa.String(), nullable=False), sa.Column("age_months", sa.Integer(), nullable=False), sa.Column("sex", sa.String(), nullable=False), sa.Column("city", sa.String(), nullable=False), sa.Column("state", sa.String(), nullable=False), sa.Column("fiv_status", sa.Boolean(), nullable=False, server_default=sa.text("false")), sa.Column("felv_status", sa.Boolean(), nullable=False, server_default=sa.text("false")), sa.Column("castrated", sa.Boolean(), nullable=False, server_default=sa.text("false")), sa.Column("vaccinated", sa.Boolean(), nullable=False, server_default=sa.text("false")), sa.Column("dewormed", sa.Boolean(), nullable=False, server_default=sa.text("false")), sa.Column("health_needs", sa.Text()), sa.Column("sociability", sa.Integer(), nullable=False), sa.Column("energy", sa.Integer(), nullable=False), sa.Column("playfulness", sa.Integer(), nullable=False), sa.Column("personality", sa.Text()), sa.Column("backstory", sa.Text()), sa.Column("photos", postgresql.JSON(), nullable=False, server_default=sa.text("'[]'::json")), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()))
    op.create_table("adoption_applications", _id_column(), sa.Column("cat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cats.id"), nullable=False), sa.Column("applicant_name", sa.String(), nullable=False), sa.Column("applicant_email", sa.String(), nullable=False), sa.Column("applicant_phone", sa.String(), nullable=False), sa.Column("message", sa.Text()), sa.Column("accepted_terms", sa.Boolean(), nullable=False), sa.Column("status", sa.String(), nullable=False, server_default="pending"), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_table("foster_applications", _id_column(), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("existing_pets", sa.Text(), nullable=False), sa.Column("compatibility", sa.Text(), nullable=False), sa.Column("prior_experience", sa.Text(), nullable=False), sa.Column("city", sa.String(), nullable=False), sa.Column("cost_aware", sa.Boolean(), nullable=False), sa.Column("status", sa.String(), nullable=False, server_default="pending"), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_table("donation_posts", _id_column(), sa.Column("protector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("title", sa.String(), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("type", sa.String(), nullable=False), sa.Column("target_amount", sa.Float()), sa.Column("current_amount", sa.Float(), nullable=False, server_default="0"), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.create_table("partners", _id_column(), sa.Column("name", sa.String(), nullable=False), sa.Column("description", sa.Text()), sa.Column("address", sa.String(), nullable=False), sa.Column("cep", sa.String(), nullable=False), sa.Column("city", sa.String(), nullable=False), sa.Column("state", sa.String(), nullable=False), sa.Column("lat", sa.Float()), sa.Column("lng", sa.Float()), sa.Column("coupon_code", sa.String()), sa.Column("discount_pct", sa.Integer()), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")))


def downgrade() -> None:
    for table in ("partners", "donation_posts", "foster_applications", "adoption_applications", "cats", "foster_profiles", "protector_profiles", "users"):
        op.drop_table(table)
