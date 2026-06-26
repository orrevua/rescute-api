from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import CatModel
from app.domain.entities.cat import Cat
from app.domain.ports.repositories import CatRepository
from app.domain.value_objects import Sex


class CatRepositoryImpl(CatRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, cat: Cat) -> Cat:
        if cat.id is None:
            model = _to_model(cat)
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
            return _to_domain(model)
        model = await self._session.merge(_to_model(cat))
        await self._session.flush()
        await self._session.refresh(model)
        return _to_domain(model)

    async def find_by_id(self, id: UUID) -> Cat | None:
        stmt = select(CatModel).where(CatModel.id == id, CatModel.is_active.is_(True))
        model = (await self._session.execute(stmt)).scalars().first()
        return _to_domain(model) if model else None

    async def find_all(self, filters: dict) -> list[Cat]:
        stmt = select(CatModel).where(CatModel.is_active.is_(True))
        if name := filters.get("name"):
            stmt = stmt.where(CatModel.name.ilike(f"%{name}%"))
        if city := filters.get("city"):
            stmt = stmt.where(CatModel.city == city)
        if state := filters.get("state"):
            stmt = stmt.where(CatModel.state == state)
        if sex := filters.get("sex"):
            stmt = stmt.where(CatModel.sex == sex)
        if (age_min := filters.get("age_min")) is not None:
            stmt = stmt.where(CatModel.age_months >= age_min)
        if (age_max := filters.get("age_max")) is not None:
            stmt = stmt.where(CatModel.age_months <= age_max)
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(m) for m in models]

    async def delete(self, id: UUID) -> None:
        stmt = select(CatModel).where(CatModel.id == id)
        model = (await self._session.execute(stmt)).scalars().first()
        if model:
            model.is_active = False
            await self._session.flush()

    async def find_by_protector(self, protector_id: UUID) -> list[Cat]:
        stmt = select(CatModel).where(
            CatModel.protector_id == protector_id, CatModel.is_active.is_(True)
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(m) for m in models]


def _to_domain(model: CatModel) -> Cat:
    return Cat(
        id=model.id,
        protector_id=model.protector_id,
        name=model.name,
        age_months=model.age_months,
        sex=Sex(model.sex),
        city=model.city,
        state=model.state,
        fiv_status=model.fiv_status,
        felv_status=model.felv_status,
        castrated=model.castrated,
        vaccinated=model.vaccinated,
        dewormed=model.dewormed,
        health_needs=model.health_needs,
        sociability=model.sociability,
        energy=model.energy,
        playfulness=model.playfulness,
        personality=model.personality,
        backstory=model.backstory,
        photos=model.photos or [],
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_model(cat: Cat) -> CatModel:
    return CatModel(
        id=cat.id,
        protector_id=cat.protector_id,
        name=cat.name,
        age_months=cat.age_months,
        sex=cat.sex.value,
        city=cat.city,
        state=cat.state,
        fiv_status=cat.fiv_status,
        felv_status=cat.felv_status,
        castrated=cat.castrated,
        vaccinated=cat.vaccinated,
        dewormed=cat.dewormed,
        health_needs=cat.health_needs,
        sociability=cat.sociability,
        energy=cat.energy,
        playfulness=cat.playfulness,
        personality=cat.personality,
        backstory=cat.backstory,
        photos=cat.photos,
        is_active=cat.is_active,
        created_at=cat.created_at,
        updated_at=cat.updated_at,
    )
