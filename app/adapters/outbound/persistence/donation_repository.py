from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import DonationPostModel
from app.domain.entities.donation import DonationPost
from app.domain.ports.repositories import DonationPostRepository
from app.domain.value_objects import DonationType


class DonationPostRepositoryImpl(DonationPostRepository):
    def __init__(self, session: AsyncSession) -> None: self._session = session
    async def save(self, post: DonationPost) -> DonationPost:
        model = _to_model(post) if post.id is None else await self._session.merge(_to_model(post))
        if post.id is None: self._session.add(model)
        await self._session.flush()
        return _to_domain(model)
    async def find_by_id(self, id):
        model = await self._session.get(DonationPostModel, id)
        return _to_domain(model) if model else None
    async def find_all(self, filters: dict) -> list[DonationPost]:
        stmt = select(DonationPostModel).where(DonationPostModel.is_active.is_(True))
        if donation_type := filters.get('type'): stmt = stmt.where(DonationPostModel.type == donation_type)
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(model) for model in models]


def _to_domain(model: DonationPostModel) -> DonationPost:
    return DonationPost(id=model.id, protector_id=model.protector_id, title=model.title, description=model.description, type=DonationType(model.type), target_amount=model.target_amount, current_amount=model.current_amount, is_active=model.is_active, created_at=model.created_at)
def _to_model(post: DonationPost) -> DonationPostModel:
    return DonationPostModel(id=post.id, protector_id=post.protector_id, title=post.title, description=post.description, type=post.type.value, target_amount=post.target_amount, current_amount=post.current_amount, is_active=post.is_active, created_at=post.created_at)
