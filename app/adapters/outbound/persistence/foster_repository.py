from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import FosterApplicationModel
from app.domain.entities.foster import FosterApplication
from app.domain.ports.repositories import FosterApplicationRepository
from app.domain.value_objects import ApplicationStatus


class FosterRepositoryImpl(FosterApplicationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, application: FosterApplication) -> FosterApplication:
        if application.id is None:
            model = _to_model(application)
            self._session.add(model)
            await self._session.flush()
            return _to_domain(model)
        model = await self._session.merge(_to_model(application))
        await self._session.flush()
        return _to_domain(model)

    async def find_by_id(self, id: UUID) -> FosterApplication | None:
        model = await self._session.get(FosterApplicationModel, id)
        return _to_domain(model) if model else None

    async def find_by_user(self, user_id: UUID) -> list[FosterApplication]:
        stmt = select(FosterApplicationModel).where(FosterApplicationModel.user_id == user_id)
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(model) for model in models]

    async def find_all(self) -> list[FosterApplication]:
        models = (await self._session.execute(select(FosterApplicationModel))).scalars().all()
        return [_to_domain(model) for model in models]


def _to_domain(model: FosterApplicationModel) -> FosterApplication:
    return FosterApplication(id=model.id, user_id=model.user_id, existing_pets=model.existing_pets, compatibility=model.compatibility, prior_experience=model.prior_experience, city=model.city, cost_aware=model.cost_aware, status=ApplicationStatus(model.status), created_at=model.created_at)


def _to_model(application: FosterApplication) -> FosterApplicationModel:
    return FosterApplicationModel(id=application.id, user_id=application.user_id, existing_pets=application.existing_pets, compatibility=application.compatibility, prior_experience=application.prior_experience, city=application.city, cost_aware=application.cost_aware, status=application.status.value, created_at=application.created_at)
