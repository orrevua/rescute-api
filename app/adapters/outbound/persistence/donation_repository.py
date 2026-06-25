from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import DonationIntentModel, DonationPostModel
from app.domain.entities.donation import DonationIntent, DonationPost
from app.domain.ports.repositories import DonationPostRepository
from app.domain.value_objects import DonationType


class DonationPostRepositoryImpl(DonationPostRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, post: DonationPost) -> DonationPost:
        model = _to_model(post) if post.id is None else await self._session.merge(_to_model(post))
        if post.id is None:
            self._session.add(model)
        await self._session.flush()
        return _to_domain(model)

    async def find_by_id(self, id: UUID) -> DonationPost | None:
        model = await self._session.get(DonationPostModel, id)
        return _to_domain(model) if model else None

    async def find_all(self, filters: dict) -> list[DonationPost]:
        stmt = select(DonationPostModel).where(DonationPostModel.is_active.is_(True))
        if donation_type := filters.get("type"):
            stmt = stmt.where(DonationPostModel.type == donation_type)
        models = (await self._session.execute(stmt)).scalars().all()
        return [_to_domain(model) for model in models]

    async def save_intent(self, intent: DonationIntent) -> DonationIntent:
        model = DonationIntentModel(
            donation_id=intent.donation_id,
            donor_name=intent.donor_name,
            donor_email=intent.donor_email,
            donor_phone=intent.donor_phone,
            amount=intent.amount,
            message=intent.message,
        )
        self._session.add(model)
        await self._session.flush()
        return _intent_to_domain(model)

    async def find_intents_by_protector(self, protector_id: UUID) -> list[DonationIntent]:
        stmt = (
            select(DonationIntentModel)
            .join(DonationPostModel)
            .where(DonationPostModel.protector_id == protector_id)
            .order_by(DonationIntentModel.created_at.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_intent_to_domain(model) for model in models]


def _to_domain(model: DonationPostModel) -> DonationPost:
    return DonationPost(
        id=model.id,
        protector_id=model.protector_id,
        title=model.title,
        description=model.description,
        type=DonationType(model.type),
        target_amount=model.target_amount,
        current_amount=model.current_amount,
        payment_link=model.payment_link,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def _to_model(post: DonationPost) -> DonationPostModel:
    return DonationPostModel(
        id=post.id,
        protector_id=post.protector_id,
        title=post.title,
        description=post.description,
        type=post.type.value,
        target_amount=post.target_amount,
        current_amount=post.current_amount,
        payment_link=post.payment_link,
        is_active=post.is_active,
        created_at=post.created_at,
    )


def _intent_to_domain(model: DonationIntentModel) -> DonationIntent:
    return DonationIntent(
        id=model.id,
        donation_id=model.donation_id,
        donor_name=model.donor_name,
        donor_email=model.donor_email,
        donor_phone=model.donor_phone,
        amount=model.amount,
        message=model.message,
        created_at=model.created_at,
    )
