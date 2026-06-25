from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import AdoptionApplicationModel, CatModel
from app.domain.entities.adoption import AdoptionApplication
from app.domain.ports.repositories import AdoptionRepository
from app.domain.value_objects import ApplicationStatus


class AdoptionRepositoryImpl(AdoptionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, application: AdoptionApplication) -> AdoptionApplication:
        if application.id is None:
            model = _to_model(application)
            self._session.add(model)
            await self._session.flush()
            return _to_domain(model)
        model = await self._session.merge(_to_model(application))
        await self._session.flush()
        return _to_domain(model)

    async def find_by_id(self, id: UUID) -> AdoptionApplication | None:
        model = await self._session.get(AdoptionApplicationModel, id)
        return _to_domain(model) if model else None

    async def find_by_cat(self, cat_id: UUID) -> list[AdoptionApplication]:
        stmt = select(AdoptionApplicationModel).where(AdoptionApplicationModel.cat_id == cat_id)
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(model) for model in models]

    async def find_by_protector_cats(self, protector_id: UUID) -> list[AdoptionApplication]:
        stmt = (
            select(AdoptionApplicationModel)
            .join(CatModel)
            .where(CatModel.protector_id == protector_id)
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(model) for model in models]


def _to_domain(model: AdoptionApplicationModel) -> AdoptionApplication:
    return AdoptionApplication(
        id=model.id,
        cat_id=model.cat_id,
        applicant_name=model.applicant_name,
        applicant_email=model.applicant_email,
        applicant_phone=model.applicant_phone,
        message=model.message,
        accepted_terms=model.accepted_terms,
        status=ApplicationStatus(model.status),
        created_at=model.created_at,
    )


def _to_model(application: AdoptionApplication) -> AdoptionApplicationModel:
    return AdoptionApplicationModel(
        id=application.id,
        cat_id=application.cat_id,
        applicant_name=application.applicant_name,
        applicant_email=application.applicant_email,
        applicant_phone=application.applicant_phone,
        message=application.message,
        accepted_terms=application.accepted_terms,
        status=application.status.value,
        created_at=application.created_at,
    )
