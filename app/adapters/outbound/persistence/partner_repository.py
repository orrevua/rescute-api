from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.outbound.persistence.models import PartnerModel, PartnerNegotiationModel
from app.domain.entities.partner import Partner, PartnerNegotiation
from app.domain.ports.repositories import PartnerRepository
from app.domain.value_objects import NegotiationStatus


class PartnerRepositoryImpl(PartnerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, partner: Partner) -> Partner:
        model = _to_model(partner) if partner.id is None else await self._session.merge(_to_model(partner))
        if partner.id is None:
            self._session.add(model)
        await self._session.flush()
        return _to_domain(model)

    async def find_all(self) -> list[Partner]:
        models = (
            await self._session.execute(
                select(PartnerModel).where(
                    PartnerModel.is_active.is_(True), PartnerModel.owner_id.isnot(None)
                )
            )
        ).scalars().all()
        return [_to_domain(model) for model in models]

    async def find_by_id(self, id: UUID) -> Partner | None:
        model = await self._session.get(PartnerModel, id)
        return _to_domain(model) if model else None

    async def find_by_location(self, lat: float, lng: float, radius: float) -> list[Partner]:
        return await self.find_all()

    async def delete(self, id: UUID) -> None:
        model = await self._session.get(PartnerModel, id)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def save_negotiation(self, negotiation: PartnerNegotiation) -> PartnerNegotiation:
        model = PartnerNegotiationModel(
            id=negotiation.id,
            partner_id=negotiation.partner_id,
            host_id=negotiation.host_id,
            proposed_amount=negotiation.proposed_amount,
            proposed_message=negotiation.proposed_message,
            contact_email=negotiation.contact_email,
            contact_phone=negotiation.contact_phone,
            status=negotiation.status.value,
            counter_amount=negotiation.counter_amount,
            counter_message=negotiation.counter_message,
            created_at=negotiation.created_at,
        )
        if negotiation.id is None:
            self._session.add(model)
        else:
            model = await self._session.merge(model)
        await self._session.flush()
        return _negotiation_to_domain(model)

    async def find_negotiation_by_id(self, id: UUID) -> PartnerNegotiation | None:
        model = await self._session.get(PartnerNegotiationModel, id)
        return _negotiation_to_domain(model) if model else None

    async def find_negotiations_by_host(self, host_id: UUID) -> list[PartnerNegotiation]:
        stmt = (
            select(PartnerNegotiationModel)
            .where(PartnerNegotiationModel.host_id == host_id)
            .order_by(PartnerNegotiationModel.created_at.desc())
        )
        models = (await self._session.execute(stmt)).scalars().all()
        return [_negotiation_to_domain(model) for model in models]


def _to_domain(model: PartnerModel) -> Partner:
    return Partner(
        id=model.id,
        name=model.name,
        description=model.description,
        address=model.address,
        cep=model.cep,
        city=model.city,
        state=model.state,
        lat=model.lat,
        lng=model.lng,
        coupon_code=model.coupon_code,
        discount_pct=model.discount_pct,
        is_active=model.is_active,
        owner_id=model.owner_id,
    )


def _to_model(partner: Partner) -> PartnerModel:
    return PartnerModel(
        id=partner.id,
        name=partner.name,
        description=partner.description,
        address=partner.address,
        cep=partner.cep,
        city=partner.city,
        state=partner.state,
        lat=partner.lat,
        lng=partner.lng,
        coupon_code=partner.coupon_code,
        discount_pct=partner.discount_pct,
        is_active=partner.is_active,
        owner_id=partner.owner_id,
    )


def _negotiation_to_domain(model: PartnerNegotiationModel) -> PartnerNegotiation:
    return PartnerNegotiation(
        id=model.id,
        partner_id=model.partner_id,
        host_id=model.host_id,
        proposed_amount=model.proposed_amount,
        proposed_message=model.proposed_message,
        contact_email=model.contact_email,
        contact_phone=model.contact_phone,
        status=NegotiationStatus(model.status),
        counter_amount=model.counter_amount,
        counter_message=model.counter_message,
        created_at=model.created_at,
    )
