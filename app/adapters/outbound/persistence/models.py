import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.outbound.persistence.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.text("true"))
    token_version: Mapped[int] = mapped_column(
        default=0, server_default=sa.text("0"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=sa.func.now(), server_default=sa.func.now()
    )

    protector_profile: Mapped["ProtectorProfileModel | None"] = relationship(
        back_populates="user"
    )
    foster_profile: Mapped["FosterProfileModel | None"] = relationship(
        back_populates="user"
    )
    cats: Mapped[list["CatModel"]] = relationship(back_populates="protector")
    foster_applications: Mapped[list["FosterApplicationModel"]] = relationship(
        back_populates="user"
    )
    donation_posts: Mapped[list["DonationPostModel"]] = relationship(
        back_populates="protector"
    )


class ProtectorProfileModel(Base):
    __tablename__ = "protector_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    org_name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(nullable=True)
    city: Mapped[str | None] = mapped_column(nullable=True)
    state: Mapped[str | None] = mapped_column(nullable=True)

    user: Mapped["UserModel"] = relationship(back_populates="protector_profile")


class FosterProfileModel(Base):
    __tablename__ = "foster_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="foster_profile")


class CatModel(Base):
    __tablename__ = "cats"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    protector_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    age_months: Mapped[int] = mapped_column(nullable=False)
    sex: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    fiv_status: Mapped[bool] = mapped_column(default=False, server_default=sa.text("false"))
    felv_status: Mapped[bool] = mapped_column(default=False, server_default=sa.text("false"))
    castrated: Mapped[bool] = mapped_column(default=False, server_default=sa.text("false"))
    vaccinated: Mapped[bool] = mapped_column(default=False, server_default=sa.text("false"))
    dewormed: Mapped[bool] = mapped_column(default=False, server_default=sa.text("false"))
    health_needs: Mapped[str | None] = mapped_column(Text, nullable=True)
    sociability: Mapped[int] = mapped_column(nullable=False)
    energy: Mapped[int] = mapped_column(nullable=False)
    playfulness: Mapped[int] = mapped_column(nullable=False)
    personality: Mapped[str | None] = mapped_column(Text, nullable=True)
    backstory: Mapped[str | None] = mapped_column(Text, nullable=True)
    photos: Mapped[list] = mapped_column(JSON, default=list, server_default=sa.text("'[]'::json"))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.text("true"))
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=sa.func.now(), server_default=sa.func.now()
    )

    protector: Mapped["UserModel"] = relationship(back_populates="cats")
    adoption_applications: Mapped[list["AdoptionApplicationModel"]] = relationship(
        back_populates="cat"
    )


class AdoptionApplicationModel(Base):
    __tablename__ = "adoption_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    cat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cats.id"), nullable=False
    )
    applicant_name: Mapped[str] = mapped_column(nullable=False)
    applicant_email: Mapped[str] = mapped_column(nullable=False)
    applicant_phone: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    accepted_terms: Mapped[bool] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(
        default="pending", server_default=sa.text("'pending'")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())

    cat: Mapped["CatModel"] = relationship(back_populates="adoption_applications")


class FosterApplicationModel(Base):
    __tablename__ = "foster_applications"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    existing_pets: Mapped[str] = mapped_column(Text, nullable=False)
    compatibility: Mapped[str] = mapped_column(Text, nullable=False)
    prior_experience: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    cost_aware: Mapped[bool] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(
        default="pending", server_default=sa.text("'pending'")
    )
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())

    user: Mapped["UserModel"] = relationship(back_populates="foster_applications")


class DonationPostModel(Base):
    __tablename__ = "donation_posts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    protector_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    target_amount: Mapped[float | None] = mapped_column(nullable=True)
    current_amount: Mapped[float] = mapped_column(default=0.0, server_default=sa.text("0"))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.text("true"))
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())

    payment_link: Mapped[str | None] = mapped_column(nullable=True)

    protector: Mapped["UserModel"] = relationship(back_populates="donation_posts")
    intents: Mapped[list["DonationIntentModel"]] = relationship(back_populates="donation_post")


class DonationIntentModel(Base):
    __tablename__ = "donation_intents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    donation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("donation_posts.id"), nullable=False
    )
    donor_name: Mapped[str] = mapped_column(nullable=False)
    donor_email: Mapped[str] = mapped_column(nullable=False)
    donor_phone: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())

    donation_post: Mapped["DonationPostModel"] = relationship(back_populates="intents")


class PartnerModel(Base):
    __tablename__ = "partners"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(nullable=False)
    cep: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    lat: Mapped[float | None] = mapped_column(nullable=True)
    lng: Mapped[float | None] = mapped_column(nullable=True)
    coupon_code: Mapped[str | None] = mapped_column(nullable=True)
    discount_pct: Mapped[int | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.text("true"))
    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class PartnerNegotiationModel(Base):
    __tablename__ = "partner_negotiations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=sa.text("gen_random_uuid()")
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("partners.id"), nullable=False
    )
    host_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    proposed_amount: Mapped[float] = mapped_column(nullable=False)
    proposed_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str] = mapped_column(nullable=False)
    contact_phone: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(
        default="pending", server_default=sa.text("'pending'")
    )
    counter_amount: Mapped[float | None] = mapped_column(nullable=True)
    counter_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())
