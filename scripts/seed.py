"""Seed a Rescute database with representative demo data.

Idempotent per record: safe to run repeatedly (it also runs at app startup
when SEED_DEMO_DATA=1). Users are upserted by email; cats, partners, and
donation posts are inserted only when a record with the same name/title
does not already exist.
"""

import asyncio

from passlib.context import CryptContext
from sqlalchemy import select, update

from app.adapters.outbound.persistence.database import Base, async_session, engine
from app.adapters.outbound.persistence.models import (
    CatModel,
    DonationPostModel,
    FosterProfileModel,
    PartnerModel,
    ProtectorProfileModel,
    UserModel,
)

SEED_EMAIL = "protetor@rescute.app"
LEGACY_SEED_EMAIL = "protetor@rescute.local"
FOSTER_EMAIL = "foster@rescute.app"
SEED_PASSWORD = "Rescute123!"
_passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _cats(protector_id) -> list[CatModel]:
    return [
        # Baseline healthy adult — the "easy adoption" case
        CatModel(
            protector_id=protector_id, name="Luna", age_months=18, sex="female",
            city="São Paulo", state="SP", sociability=5, energy=3, playfulness=4,
            vaccinated=True, dewormed=True, castrated=True,
            personality="Affectionate and curious",
            backstory="Rescued from a parking lot as a kitten, fully socialized.",
            photos=[],
        ),
        # Kitten, incomplete health record — tests unvaccinated/uncastrated display
        CatModel(
            protector_id=protector_id, name="Miso", age_months=3, sex="male",
            city="São Paulo", state="SP", sociability=4, energy=5, playfulness=5,
            vaccinated=False, dewormed=True, castrated=False,
            personality="Tiny tornado, plays until he drops",
            backstory="Found alone in a cardboard box; still completing his first vaccine cycle.",
            photos=[],
        ),
        # Senior cat — tests high-age rendering and calm profile
        CatModel(
            protector_id=protector_id, name="Dona Rosa", age_months=132, sex="female",
            city="Campinas", state="SP", sociability=3, energy=1, playfulness=2,
            vaccinated=True, dewormed=True, castrated=True,
            personality="Quiet lap cat, sleeps most of the day",
            backstory="Surrendered when her elderly owner moved into care.",
            photos=[],
        ),
        # FIV-positive with ongoing health needs — tests health flags and needs text
        CatModel(
            protector_id=protector_id, name="Pirata", age_months=48, sex="male",
            city="São Paulo", state="SP", sociability=4, energy=2, playfulness=3,
            fiv_status=True, vaccinated=True, dewormed=True, castrated=True,
            health_needs="FIV-positive; needs indoor-only home and yearly bloodwork.",
            personality="Gentle one-eyed veteran of the streets",
            backstory="Lost an eye in a street fight before rescue; FIV under control.",
            photos=[],
        ),
        # FeLV-positive — the harder-to-place medical case
        CatModel(
            protector_id=protector_id, name="Nina", age_months=24, sex="female",
            city="Guarulhos", state="SP", sociability=5, energy=3, playfulness=4,
            felv_status=True, vaccinated=True, dewormed=True, castrated=True,
            health_needs="FeLV-positive; must be an only cat or live with other FeLV+ cats.",
            personality="People-oriented, follows you everywhere",
            photos=[],
        ),
        # Shy/low-sociability — tests the low end of the trait scales
        CatModel(
            protector_id=protector_id, name="Sombra", age_months=36, sex="male",
            city="São Paulo", state="SP", sociability=1, energy=2, playfulness=1,
            vaccinated=True, dewormed=False, castrated=True,
            personality="Very shy, needs a patient adopter and a quiet home",
            backstory="Semi-feral rescue; warming up slowly to humans.",
            photos=[],
        ),
        # Different state — tests location filtering
        CatModel(
            protector_id=protector_id, name="Tangerina", age_months=10, sex="female",
            city="Rio de Janeiro", state="RJ", sociability=4, energy=4, playfulness=5,
            vaccinated=True, dewormed=True, castrated=False,
            personality="Orange, loud, and convinced she runs the house",
            photos=[],
        ),
    ]


def _partners() -> list[PartnerModel]:
    return [
        PartnerModel(
            name="Clínica Patas Livres", address="Rua das Flores, 123", cep="01000-000",
            city="São Paulo", state="SP", description="Partner veterinary clinic",
            discount_pct=10, coupon_code="RESCUTE10",
        ),
        PartnerModel(
            name="PetShop Bigode", address="Av. Paulista, 900", cep="01310-100",
            city="São Paulo", state="SP", description="Food and supplies for adopters",
            discount_pct=15, coupon_code="BIGODE15",
        ),
        # No discount/coupon — tests optional-field rendering
        PartnerModel(
            name="Hotelzinho Miau", address="Rua do Catete, 45", cep="22220-000",
            city="Rio de Janeiro", state="RJ",
            description="Cat boarding partner (no standing discount)",
        ),
    ]


def _donation_posts(protector_id) -> list[DonationPostModel]:
    return [
        # Financial with target, partially funded
        DonationPostModel(
            protector_id=protector_id, title="Ração para o inverno",
            description="Help stock the shelter with food for winter.",
            type="financial", target_amount=1500, current_amount=420,
        ),
        # Financial, nothing raised yet — tests the 0% progress state
        DonationPostModel(
            protector_id=protector_id, title="Pirata's yearly bloodwork",
            description="FIV+ cats need annual exams to stay healthy.",
            type="financial", target_amount=350, current_amount=0,
        ),
        # Item type, no monetary target — tests non-financial posts
        DonationPostModel(
            protector_id=protector_id, title="Blankets and carriers",
            description="Used blankets, towels, and transport carriers welcome.",
            type="item", target_amount=None, current_amount=0,
        ),
    ]


async def _upsert_user(session, email: str, role: str, legacy_email: str | None = None) -> UserModel:
    lookup = [email] + ([legacy_email] if legacy_email else [])
    user = await session.scalar(select(UserModel).where(UserModel.email.in_(lookup)))
    if not user:
        user = UserModel(email=email, hashed_password=_passwords.hash(SEED_PASSWORD), role=role)
        session.add(user)
        await session.flush()
    else:
        user.email = email
        user.hashed_password = _passwords.hash(SEED_PASSWORD)
    return user


async def seed() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        protector = await _upsert_user(session, SEED_EMAIL, "protector", LEGACY_SEED_EMAIL)
        foster = await _upsert_user(session, FOSTER_EMAIL, "foster")

        if not await session.scalar(
            select(ProtectorProfileModel).where(ProtectorProfileModel.user_id == protector.id)
        ):
            session.add(
                ProtectorProfileModel(
                    user_id=protector.id,
                    org_name="Rescute São Paulo",
                    description="Demo account managing the seed cats.",
                    city="São Paulo",
                    state="SP",
                )
            )

        if not await session.scalar(
            select(FosterProfileModel).where(FosterProfileModel.user_id == foster.id)
        ):
            session.add(
                FosterProfileModel(
                    user_id=foster.id,
                    full_name="Fê Foster",
                    phone="+55 11 99999-0000",
                    city="São Paulo",
                    state="SP",
                )
            )

        existing_cats = set(
            (await session.scalars(select(CatModel.name).where(CatModel.protector_id == protector.id))).all()
        )
        session.add_all(cat for cat in _cats(protector.id) if cat.name not in existing_cats)

        existing_partners = set((await session.scalars(select(PartnerModel.name))).all())
        session.add_all(p for p in _partners() if p.name not in existing_partners)

        # Repair rows a previous seed created with a type outside the
        # DonationType enum ("supplies"), which crashed donation listings.
        await session.execute(
            update(DonationPostModel)
            .where(DonationPostModel.type.notin_(["financial", "item"]))
            .values(type="item")
        )

        existing_posts = set(
            (await session.scalars(select(DonationPostModel.title).where(DonationPostModel.protector_id == protector.id))).all()
        )
        session.add_all(d for d in _donation_posts(protector.id) if d.title not in existing_posts)

        await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
