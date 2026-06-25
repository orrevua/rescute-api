"""Seed a local Rescute database with representative development data."""

import asyncio

from passlib.context import CryptContext
from sqlalchemy import select

from app.adapters.outbound.persistence.database import Base, async_session, engine
from app.adapters.outbound.persistence.models import (
    CatModel,
    DonationPostModel,
    PartnerModel,
    ProtectorProfileModel,
    UserModel,
)

SEED_EMAIL = "protetor@rescute.app"
LEGACY_SEED_EMAIL = "protetor@rescute.local"
SEED_PASSWORD = "Rescute123!"
_passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        protector = await session.scalar(
            select(UserModel).where(UserModel.email.in_([SEED_EMAIL, LEGACY_SEED_EMAIL]))
        )
        if not protector:
            protector = UserModel(
                email=SEED_EMAIL,
                hashed_password=_passwords.hash(SEED_PASSWORD),
                role="protector",
            )
            session.add(protector)
            await session.flush()
        else:
            protector.email = SEED_EMAIL
            protector.hashed_password = _passwords.hash(SEED_PASSWORD)

        profile = await session.scalar(
            select(ProtectorProfileModel).where(
                ProtectorProfileModel.user_id == protector.id
            )
        )
        if not profile:
            session.add(
                ProtectorProfileModel(
                    user_id=protector.id,
                    org_name="Rescute São Paulo",
                    description="Conta de desenvolvimento para gerir a Luna.",
                    city="São Paulo",
                    state="SP",
                )
            )

        if not await session.scalar(select(CatModel.id).limit(1)):
            session.add_all([
                CatModel(protector_id=protector.id, name="Luna", age_months=18, sex="female", city="São Paulo", state="SP", sociability=5, energy=3, playfulness=4, vaccinated=True, dewormed=True, castrated=True, personality="Carinhosa e curiosa", photos=[]),
                PartnerModel(name="Clínica Patas Livres", address="Rua das Flores, 123", cep="01000-000", city="São Paulo", state="SP", description="Atendimento parceiro", discount_pct=10),
                DonationPostModel(protector_id=protector.id, title="Ração para o inverno", description="Ajude a abastecer o abrigo.", type="financial", target_amount=1500, current_amount=420),
            ])

        await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
